/*
go build -gcflags="all=-N -l" daily_handler.go
dlv exec daily_handler -- --action daily_json_to_hr --src "/Users/alexey.beley/git/horey/human_api/horey/human_api/go/daily_report_sample.json" --dst "dst_file_path"
go run . --action daily_json_to_hr --src "/Users/alexey.beley/git/horey/human_api/horey/human_api/go/daily_report_sample.json" --dst "dst_file_path"
*/
package main

import (
	"reflect"
	"testing"
	"path/filepath"
	"os"
	"log"
	"bytes"
	"io"
)

var test_WorkerDailyReport = WorkerDailyReport{
	WorkerID: "horey",
	New:      []WorkerWobjReport{{Parent: []string{"1", "2", "3"}, Child: []string{"4", "5", "6"}}},
	Active:   []WorkerWobjReport{},
	Blocked:  []WorkerWobjReport{},
	Closed:   []WorkerWobjReport{},
}

func TestInitWorkerDailyReport(t *testing.T) {
	t.Run("Init test", func(t *testing.T) {
		if test_WorkerDailyReport.WorkerID != "horey" {
			t.Errorf("ConvertDailyJsonToHR() = %v, want %v", test_WorkerDailyReport.WorkerID, "WorkerID")
		}
	})
}

var test_WorkerDailyReports = []WorkerDailyReport{
	{WorkerID: "horey",
		New: []WorkerWobjReport{
			{
				Parent: []string{"UserStory", "1", "test User story"},
				Child:  []string{"Task", "11", "test Task"},
				Comment: "Standard Comment",
				InvestedTime: 1,
				LeftTime: 1,
			},
			{
				Parent: []string{"UserStory", "1", "test User story"},
				Child:  []string{"Task", "12", "test Task 2"},
				Comment: "start_comment Standard, Comment end_comment",
				InvestedTime: 0,
				LeftTime: 1,
			},
		},
		Active: []WorkerWobjReport{
			{
				Parent: []string{"UserStory", "2", "test User story2"},
				Child:  []string{"Task", "22", "test Task 22"},
				Comment: "start_comment Standard, Comment end_comment",
				InvestedTime: 1,
				LeftTime: 0,
			},
		},
		Blocked: []WorkerWobjReport{
			{
				Parent: []string{"UserStory", "2", "test User story2"},
				Child:  []string{"Task", "23", "test Task 23"},
				Comment: "start_comment Standard, Comment end_comment",
				InvestedTime: 0,
				LeftTime: 0,
			},
		},
		Closed: []WorkerWobjReport{
	         {
				Parent: []string{"UserStory", "3", "test User story3"},
				Child:  []string{"Task", "31", "test Task 31"},
				Comment: "",
				InvestedTime: 0,
				LeftTime: 0,
			 },
		},
	},
}

func TestInitListOfWorkerDailyReport(t *testing.T) {
	t.Run("Init test", func(t *testing.T) {
		if len(test_WorkerDailyReports) != 1 {
			t.Errorf("ConvertDailyJsonToHR() = %v, want %v", test_WorkerDailyReport.WorkerID, "WorkerID")
		}
	})
}


const chunkSize = 64000

func DeepCompare(file1, file2 string) bool {
    // Check files content identical

    f1, err := os.Open(file1)
    if err != nil {
        log.Fatal(err)
    }
    defer f1.Close()

    f2, err := os.Open(file2)
    if err != nil {
        log.Fatal(err)
    }
    defer f2.Close()

    for {
        b1 := make([]byte, chunkSize)
        _, err1 := f1.Read(b1)

        b2 := make([]byte, chunkSize)
        _, err2 := f2.Read(b2)

        if err1 != nil || err2 != nil {
            if err1 == io.EOF && err2 == io.EOF {
                return true
            } else if err1 == io.EOF || err2 == io.EOF {
                return false
            } else {
                log.Fatal(err1, err2)
            }
        }

        if !bytes.Equal(b1, b2) {
            return false
        }
    }
}

func GetTestHapiFilePath(basename string) (string, error){
   cwd_path, err:= os.Getwd()
   if err != nil {
       return "", err
   }
   abs_path, err := filepath.Abs(cwd_path)
   if err != nil {
       return "", err
   }
   if base == "" {
   basename = "test.hapi"
   }
   dst_file_path := filepath.Join(abs_path, basename)
   log.Printf("Generated test destination HAPI file path: %s", dst_file_path)
   return dst_file_path, nil

}

func TestConvertDailyJsonToHR(t *testing.T) {
	tests := []struct {
		name     string
		filename string
		want     []WorkerDailyReport
		wantErr  bool
	}{
		{
			name:     "Valid JSON invalid data",
			filename: "daily_report_sample.json", // Create this test file
			want:     []WorkerDailyReport{test_WorkerDailyReport},
			wantErr:  true,
		},
		{
			name:     "Valid JSON valid data",
			filename: "daily_report_sample.json", // Create this test file
			want:     test_WorkerDailyReports,
			wantErr:  false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ConvertDailyJsonToHR(tt.filename, "dst_file_path")

			if (err != nil) && !tt.wantErr {
				t.Errorf("readItemsFromFile() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			if !reflect.DeepEqual(got, tt.want) && !tt.wantErr {
				t.Errorf("ConvertDailyJsonToHR() = %v, want %v", got, tt.want)
			}
		})
	}
}


func TestWriteDailyToHRFile(t *testing.T){
   t.Run("Valid file", func (t *testing.T){
   dst_file_path, err := GetTestHapiFilePath("")
      if err != nil {
       t.Errorf("Error getting hapi file pathpath: %s", err)
       return
   }

   want_file_path := filepath.Join(filepath.Dir(dst_file_path), "test_want.hapi")

   _, err = WriteDailyToHRFile(test_WorkerDailyReports, dst_file_path)
   if err != nil {
       t.Errorf("Was not able to generate reports hapi: %s", err)
       return
   }

   if !DeepCompare(want_file_path, dst_file_path){
     t.Errorf("Generated file %v is not equal to wanted %v", dst_file_path, want_file_path)
   }
   })
}

func TestWriteWorkerWobjStatusDailyToHRFile(t *testing.T){
    t.Run("Valid wobject", func(t *testing.T){
      dst_file_path, err := GetTestHapiFilePath("")
      if err != nil {
       t.Errorf("Error getting hapi file path: %s", err)
       return
      }
      	file, err := os.OpenFile(dst_file_path, os.O_TRUNC|os.O_CREATE|os.O_WRONLY, 0644)
	    if err!= nil {
	        t.Errorf("Error opening hapi file path: %s", err)
	    }

	  defer file.Close() // Ensure the file is closed when the function exits

      wobj_reports := []WorkerWobjReport{
			{
				Parent: []string{"UserStory", "1", "test User story"},
				Child:  []string{"Task", "11", "test Task"},
				Comment: "Standard Comment",
				InvestedTime: 1,
				LeftTime: 1,
			},
			{
				Parent: []string{"UserStory", "1", "test User story"},
				Child:  []string{"Task", "12", "test Task 2"},
				Comment: "start_comment Standard, Comment end_comment",
				InvestedTime: 0,
				LeftTime: 1,
			},
		}

      ok, err := WriteWorkerWobjStatusDailyToHRFile(file, "NEW", wobj_reports)
      if err != nil || !ok {
	        t.Errorf("Test failed: %s, %t", err, ok)
	    }
    })

}

//ConvertHRToDailyJson
ReadDailyFromHRFile
GetTestHapiFilePath("daily_report_sample_input.hapi")