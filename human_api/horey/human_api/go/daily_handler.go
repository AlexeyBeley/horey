/*
go build -gcflags="all=-N -l" daily_handler.go
dlv exec daily_handler -- --action daily_json_to_hr --src "/Users/alexey.beley/git/horey/human_api/horey/human_api/go/daily_report_sample.json" --dst "dst_file_path"
go run . --action daily_json_to_hr --src "/Users/alexey.beley/git/horey/human_api/horey/human_api/go/daily_report_sample.json" --dst "/Users/alexey.beley/git/horey/human_api/horey/human_api/go/daily_report_sample.hapi"

go run . --action hr_to_daily_json --src "daily_report_sample.hapi" --dst "daily_report_sample_tmp.json"
*/
package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strconv"
	"strings"
)

const delim = "!!=!!"

type WorkerWobjReport struct {
	Parent       []string `json:"parent"`
	Child        []string `json:"child"`
	Comment      string   `json:"comment"`
	InvestedTime int      `json:"invested_time"`
	LeftTime     int      `json:"left_time"`
}

type WorkerDailyReport struct {
	/*
	   {worker_id: "str"
	   new: [{"parent": (type, id, title), "child": (type, item.id, item.title)}],
	   active: [{"parent": (type, id, title), "child": (type, item.id, item.title)}],
	   blocked: [{"parent": (type, id, title), "child": (type, item.id, item.title)}],
	   closed: [{"parent": (type, id, title), "child": (type, item.id, item.title)}]
	*/
	WorkerID string             `json:"worker_id"`
	New      []WorkerWobjReport `json:"new"`
	Active   []WorkerWobjReport `json:"active"`
	Blocked  []WorkerWobjReport `json:"blocked"`
	Closed   []WorkerWobjReport `json:"closed"`
}

func main() {
	/*
	   daily_handler --action daily_json_to_hr --src --dst
	*/
	action := flag.String("action", "none", "The action to take")
	src := flag.String("src", "none", "Source file")
	dst := flag.String("dst", "none", "Destination file")

	flag.Parse()

	if *action == "daily_json_to_hr" {
		workers_daily, err := ConvertDailyJsonToHR(*src, *dst)
		if err != nil || len(workers_daily) == 0 {
			log.Fatal(err, workers_daily)
		}
	} else if *action == "hr_to_daily_json" {
		log.Fatalf("Handling action '%v'", *action)
		workers_daily, err := ConvertHRToDailyJson(*src, *dst)
		if err != nil || len(workers_daily) == 0 {
			log.Fatal(err, workers_daily)
		}
	} else {
		log.Fatalf("Unknown action '%v'", *action)
	}

}

func ConvertDailyJsonToHR(src_file_path, dst_file_path string) (reports []WorkerDailyReport, err error) {
	log.Printf("Called with src '%s' and dst '%s'", src_file_path, dst_file_path)

	data, err := ioutil.ReadFile(src_file_path)
	if err != nil {
		return nil, err
	}

	err = json.Unmarshal(data, &reports)
	if err != nil {
		return nil, err
	}

	WriteDailyToHRFile(reports, dst_file_path)

	return reports, nil
}

func WriteDailyToHRFile(reports []WorkerDailyReport, dst_file_path string) (bool, error) {
	log.Printf("Writing reports to '%s'", dst_file_path)
	worker_delim := fmt.Sprintf("%sH_ReportWorkerID%s", delim, delim)
	file, err := os.OpenFile(dst_file_path, os.O_TRUNC|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return false, err
	}
	defer file.Close() // Ensure the file is closed when the function exits

	for _, report := range reports {
		if !CheckWorkerManaged(report.WorkerID) {
			continue
		}

		fmt.Printf("Writing worker report: '%v'\n", report.WorkerID)

		line := fmt.Sprintf("%s %s\n", worker_delim, report.WorkerID)
		if _, err := file.WriteString(line); err != nil {
			return false, err
		}

		WriteWorkerWobjStatusDailyToHRFile(file, "NEW", report.New)
		WriteWorkerWobjStatusDailyToHRFile(file, "ACTIVE", report.Active)
		WriteWorkerWobjStatusDailyToHRFile(file, "BLOCKED", report.Blocked)
		WriteWorkerWobjStatusDailyToHRFile(file, "CLOSED", report.Closed)

	}
	return true, nil
}

func WriteWorkerWobjStatusDailyToHRFile(file *os.File, wobj_status string, wobj_reports []WorkerWobjReport) (bool, error) {
	line := fmt.Sprintf(">%s:\n", wobj_status)
	if _, err := file.WriteString(line); err != nil {
		return false, err
	}
	for _, wobj := range wobj_reports {
		line = fmt.Sprintf("[%s %s #%s] %s -> ", wobj.Parent[0], wobj.Parent[1], wobj.Parent[2], delim)
		if _, err := file.WriteString(line); err != nil {
			return false, err
		}

		line = fmt.Sprintf("%s %s #%s %s", wobj.Child[0], wobj.Child[1], wobj.Child[2], delim)
		if _, err := file.WriteString(line); err != nil {
			return false, err
		}

		actions_line := ""
		if wobj.LeftTime != 0 {
			actions_line = actions_line + strconv.Itoa(wobj.LeftTime)
		}

		if wobj.InvestedTime != 0 {
			if actions_line != "" {
				actions_line = actions_line + ", +" + strconv.Itoa(wobj.InvestedTime)
			} else {
				actions_line = strconv.Itoa(wobj.InvestedTime)
			}
		}

		if wobj.Comment != "" {
			if actions_line != "" {
				actions_line = actions_line + ", " + wobj.Comment
			} else {
				actions_line = wobj.Comment
			}
		}

		actions_line = " Actions: " + actions_line + "\n"
		if _, err := file.WriteString(actions_line); err != nil {
			return false, err
		}

	}
	return true, nil
}

func CheckWorkerManaged(worker_id string) bool {
	if worker_id != "" {
		return true
	}
	return false
}

func ConvertHRToDailyJson(src_file_path, dst_file_path string) (reports []WorkerDailyReport, err error) {
	log.Printf("Called with src '%s' and dst '%s'", src_file_path, dst_file_path)

	reports, err = ReadDailyFromHRFile(src_file_path)
	if err != nil {
		return nil, err
	}

	jsonData, err := json.MarshalIndent(reports, "", "  ")
	if err != nil {
		return nil, err
	}

	err = ioutil.WriteFile(dst_file_path, jsonData, 0644)

	return reports, nil
}

func ReadDailyFromHRFile(src_file_path string) ([]WorkerDailyReport, error) {
	log.Printf("Reading reports from '%s'", src_file_path)
	data, err := ioutil.ReadFile(src_file_path)
	if err != nil {
		return nil, err
	}

	report_lines := strings.Split(string(data), "\n")
	worker_chunks, err := SplitHapiLinesToWorkerChunks(report_lines)
	if err != nil || len(worker_chunks) == 0 {
		return nil, err
	}
	reports, err := ConvertWorkerChunksToWorkerDailyReports(worker_chunks)
	if err != nil || len(reports) == 0 {
		return []WorkerDailyReport{}, err
	}

	// todo: replace worker_chunks with structs ready for json
	//worker_chunks, errors.New("Not implemented")
	return reports, errors.New("Not implemented")
}

func SplitHapiLinesToWorkerChunks(lines []string) (chunks [][]string, err error) {
	worker_delim := fmt.Sprintf("%sH_ReportWorkerID%s", delim, delim)
	var worker_chunk []string
	var worker_chunks [][]string

	for _, line := range lines {
		if strings.Contains(line, worker_delim) && len(worker_chunk) > 0 {
			log.Printf("Found '%s' contains '%s'", line, worker_delim)
			worker_chunks = append(worker_chunks, worker_chunk)
			worker_chunk = []string{}
		}
		worker_chunk = append(worker_chunk, line)
	}
	if len(worker_chunk) > 0 {
		worker_chunks = append(worker_chunks, worker_chunk)
	}

	return worker_chunks, nil

}

func ConvertWorkerChunksToWorkerDailyReports(chunks [][]string) ([]WorkerDailyReport, error) {

	var reports []WorkerDailyReport

	for _, chunk := range chunks {
		report, err := ConvertWorkerChunkToWorkerDailyReport(chunk)
		if err != nil {
			return reports, err
		}
		reports = append(reports, report)
	}

	return reports, nil
}

func ConvertWorkerChunkToWorkerDailyReport(chunk []string) (report WorkerDailyReport, err error) {
	/*
		WorkerID string             `json:"worker_id"`
		New      []WorkerWobjReport `json:"new"`
		Active   []WorkerWobjReport `json:"active"`
		Blocked  []WorkerWobjReport `json:"blocked"`
		Closed   []WorkerWobjReport `json:"closed"`
	*/

	id, new, active, blocked, closed, err := SpitChunkByTypes(chunk)
	fmt.Printf("%v, %v, %v, %v, %v", id, new, active, blocked, closed)
	if err != nil {
		return report, err
	}
	return report, nil
}

func SpitChunkByTypes(lines []string) (id string, new, active, blocked, closed []string, err error) {
	new, active, blocked, closed = []string{}, []string{}, []string{}, []string{}
	worker_delim := fmt.Sprintf("%sH_ReportWorkerID%s", delim, delim)

	var aggregator string

	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.HasSuffix(line, "\n") {
			line = line[:len(line)-2]
		}

		if strings.Contains(line, worker_delim) {
			id = line[len(worker_delim):]
			continue
		}

		if line == ">NEW:" || line == ">ACTIVE:" || line == ">BLOCKED:" || line == ">CLOSED:" {
			aggregator = line
			continue
		} else {
			if aggregator == ">NEW:" {
				new = append(new, line)
			} else if aggregator == ">ACTIVE:" {
				active = append(active, line)
			} else if aggregator == ">BLOCKED:" {
				blocked = append(blocked, line)
			} else if aggregator == ">CLOSED:" {
				closed = append(closed, line)
			} else {
				return id, new, active, blocked, closed, errors.New("Unknown state" + aggregator)
			}

		}
	}

	return id, new, active, blocked, closed, nil
}

func GenerateWobjectReportFromHapiLine(line string) (WorkerWobjReport, error) {
	// "[UserStory 1 #test User story] !!=!! -> Task 11 #test Task !!=!! Actions: 1, +1, Standard Comment",

	log.Printf("GenerateWobjectReportFromHapiLine called with %s", line)
	delim_count := strings.Count(line, delim)
	if delim_count != 2 {
		return WorkerWobjReport{}, fmt.Errorf("Delimiters count expected 2, got %v", delim_count)
	}

	line_parts := strings.Split(line, delim)
	fmt.Printf("line_parts before parent: '%v'", line_parts)
	parent_substring := line_parts[0]
	parent_substring = strings.TrimPrefix(parent_substring, " ")
	parent_substring = strings.TrimSuffix(parent_substring, " ")
	if !strings.HasPrefix(parent_substring, "[") || !strings.HasSuffix(parent_substring, "]") {
		return WorkerWobjReport{}, fmt.Errorf("Parent format is wrong: '%v'", parent_substring)
	}
	parent_substring = parent_substring[1 : len(parent_substring)-1]

	parent, err := GenerateWobjectFromHapiSubLine(parent_substring)
	if err != nil {
		return WorkerWobjReport{}, err
	}
	fmt.Printf("line_parts after parent: '%v'", line_parts)
	child_substring := line_parts[1]
	child_substring = strings.TrimPrefix(child_substring, " ")
	child_substring = strings.TrimSuffix(child_substring, " ")
	if !strings.HasPrefix(child_substring, "->") {
		return WorkerWobjReport{}, fmt.Errorf("Child format is wrong: '%v'", child_substring)
	}
	child_substring = child_substring[2:]
	child, err := GenerateWobjectFromHapiSubLine(child_substring)
	if err != nil {
		return WorkerWobjReport{}, err
	}

	actions := strings.TrimPrefix(line_parts[2], " ")
	if !strings.HasPrefix(actions, "Actions:") {
		return WorkerWobjReport{}, fmt.Errorf("Wrong format, missing 'Actions:' in suffix: '%v'", actions)
	}
	actions = actions[len("Actions:"):]
	actions = strings.TrimPrefix(actions, " ")
	actions = strings.TrimSuffix(actions, " ")

	lef_time, invested_time, comment, err1 := GenerateWobjectActionsFromHapiSubLine(actions)
	if err1 != nil {
		return WorkerWobjReport{}, err1
	}

	int_invested_time, err := strconv.Atoi(invested_time)
	int_lef_time, err := strconv.Atoi(lef_time)

	wobj := WorkerWobjReport{
		Parent:       parent[:],
		Child:        child[:],
		Comment:      comment,
		InvestedTime: int_invested_time,
		LeftTime:     int_lef_time,
	}
	return wobj, nil
}

func GenerateWobjectFromHapiSubLine(line string) ([3]string, error) {
	//"UserStory 1 #test User story
	// Task 11 #test Task
	// Task #test Task
	// UserStory #title
	// UserStory -1 #title
	//log.Printf("GenerateWobjectFromHapiSubLine Called with '%s'", line)
	line = strings.TrimPrefix(line, " ")
	chunks := strings.Split(line, " ")
	wobj_type := chunks[0]
	if wobj_type != "UserStory" && wobj_type != "Task" {
		return [3]string{"", "", ""}, fmt.Errorf("Unsupported type: '%s'", wobj_type)
	}

	wobj_id := ""
	title := chunks[1][1:]
	var title_left []string

	if strings.HasPrefix(chunks[1], "#") {
		wobj_id = ""
		title = chunks[1][1:]
		title_left = chunks[2:]
	} else {
		wobj_id = chunks[1]
		if !strings.HasPrefix(chunks[2], "#") {
		}
		title = chunks[2][1:]
		title_left = chunks[3:]
	}
	if len(title_left) > 0 {
		title += " " + strings.Join(title_left, " ")
	}
	//todo:
	if wobj_type != "UserStory" && wobj_type != "Task" {
		return [3]string{"", "", ""}, fmt.Errorf("Unsupported type: '%s'", wobj_type)
	}

	return [3]string{wobj_type, wobj_id, title}, nil
}

func GenerateWobjectActionsFromHapiSubLine(line string) (lef_time, invested_time, comment string, err error) {
	line = strings.TrimPrefix(line, " ")
	line = strings.TrimSuffix(line, " ")
	if len(line) == 0 {
		return lef_time, invested_time, comment, nil
	}

	lst_parts := strings.Split(line, ",")

	first_char := lst_parts[0][0]

	_, err = strconv.Atoi(string(first_char))

	if err == nil {
		firstPart := strings.TrimPrefix(lst_parts[0], " ")
		firstPart = strings.TrimSuffix(firstPart, " ")
		number, errConvert := strconv.Atoi(firstPart)
		if errConvert != nil {
			return lef_time, invested_time, comment, errConvert
		}
		lef_time = strconv.Itoa(number)
		lst_parts = lst_parts[1:]
	}

	if len(lst_parts) == 0 {
		return lef_time, invested_time, comment, nil
	}

	firstPart := strings.TrimPrefix(lst_parts[0], " ")
	firstPart = strings.TrimSuffix(firstPart, " ")
	first_char = firstPart[0]
	if first_char == '+' {
		firstPart = firstPart[1:]
		number, errConvert := strconv.Atoi(firstPart)
		if errConvert != nil {
			return lef_time, invested_time, comment, errConvert
		}
		invested_time = strconv.Itoa(number)
		lst_parts = lst_parts[1:]
	}

	if len(lst_parts) == 0 {
		return lef_time, invested_time, comment, nil
	}
	comment = strings.Join(lst_parts, ",")
	comment = strings.TrimSuffix(strings.TrimPrefix(comment, " "), " ")

	return lef_time, invested_time, comment, nil
}
