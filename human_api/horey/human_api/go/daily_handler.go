/*
go build -gcflags="all=-N -l" daily_handler.go
dlv exec daily_handler -- --action daily_json_to_hr --src "/Users/alexey.beley/git/horey/human_api/horey/human_api/go/daily_report_sample.json" --dst "dst_file_path"
go run . --action daily_json_to_hr --src "/Users/alexey.beley/git/horey/human_api/horey/human_api/go/daily_report_sample.json" --dst "/Users/alexey.beley/git/horey/human_api/horey/human_api/go/daily_report_sample.hapi"
*/
package main

import (
	"encoding/json"
	"flag"
	"io/ioutil"
	"log"
	"os"
	"fmt"
	"strconv"
)

type WorkerWobjReport struct {
	Parent []string `json:"parent"`
	Child  []string `json:"child"`
	Comment string `json:"comment"`
	InvestedTime int `json:"invested_time"`
	LeftTime int `json:"left_time"`
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
		flag.Parse()
		workers_daily, err := ConvertDailyJsonToHR(*src, *dst)
		if err != nil || len(workers_daily) == 0 {
			log.Fatal(err, workers_daily)
		}
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

func WriteDailyToHRFile(reports []WorkerDailyReport, dst_file_path string ) (bool, error){
    delim := "!!=!!"
   	log.Printf("Writing reports to '%s'", dst_file_path)
   	file, err:= os.OpenFile(dst_file_path, os.O_TRUNC|os.O_CREATE|os.O_WRONLY, 0644)
	if err!= nil {
		return false, err
	}
	defer file.Close() // Ensure the file is closed when the function exits

   	for _, report := range reports {
   	    if !CheckWorkerManaged(report.WorkerID) {
   	        continue
   	    }

        fmt.Printf("Writing worker report: '%v'\n", report.WorkerID)

        line:= fmt.Sprintf("%sH_ReportWorkerID%s %s\n", delim, delim, report.WorkerID)
        if _, err:= file.WriteString(line); err!= nil {
            return false, err
	    }

        WriteWorkerWobjStatusDailyToHRFile(file, delim, "NEW",  report.New)
        WriteWorkerWobjStatusDailyToHRFile(file, delim, "ACTIVE",  report.Active)
        WriteWorkerWobjStatusDailyToHRFile(file, delim, "BLOCKED",  report.Blocked)
        WriteWorkerWobjStatusDailyToHRFile(file, delim, "CLOSED",  report.Closed)

    }
    return true, nil
}

func WriteWorkerWobjStatusDailyToHRFile(file *os.File, delim, wobj_status string, wobj_reports []WorkerWobjReport) (bool, error){
        line := fmt.Sprintf(">%s:\n", wobj_status)
        if _, err:= file.WriteString(line); err!= nil {
            return false, err
	    }
	    for _, wobj := range wobj_reports {
	        line = fmt.Sprintf("[%s %s #%s] %s -> ", wobj.Parent[0], wobj.Parent[1], wobj.Parent[2], delim)
	        if _, err:= file.WriteString(line); err!= nil {
                return false, err
	        }

	        line = fmt.Sprintf("%s %s #%s %s" , wobj.Child[0], wobj.Child[1], wobj.Child[2], delim)
	        if _, err:= file.WriteString(line); err!= nil {
                return false, err
	        }

            actions_line := ""
            if wobj.LeftTime != 0 {
              actions_line = actions_line + strconv.Itoa(wobj.LeftTime)
            }

            if wobj.InvestedTime != 0 {
                if actions_line != "" {
                    actions_line = actions_line + ", +"+ strconv.Itoa(wobj.InvestedTime)
                } else {
                    actions_line = strconv.Itoa(wobj.InvestedTime)
                }
            }

            if wobj.Comment != "" {
                if actions_line != ""{
                    actions_line = actions_line + ", " + wobj.Comment
                } else {
                    actions_line = wobj.Comment
                }
            }

            actions_line = " Actions: " + actions_line + "\n"
	        if _, err:= file.WriteString(actions_line); err!= nil {
                return false, err
	        }

	    }
	    return true, nil
}


func CheckWorkerManaged(worker_id string) bool{
    if (worker_id != ""){
    return true
    }
    return false
}
