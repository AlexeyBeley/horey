/*
go build -gcflags="all=-N -l" daily_handler.go
dlv exec daily_handler -- --action daily_json_to_hr --src "/Users/alexey.beley/git/horey/human_api/horey/human_api/go/daily_report_sample.json" --dst "dst_file_path"
go run . --action daily_json_to_hr --src "/Users/alexey.beley/git/horey/human_api/horey/human_api/go/daily_report_sample.json" --dst "dst_file_path"
*/
package main

import (
	"reflect"
	"testing"
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
			},
			{
				Parent: []string{"UserStory", "1", "test User story"},
				Child:  []string{"Task", "12", "test Task 2"},
			},
		},
		Active: []WorkerWobjReport{
			{
				Parent: []string{"UserStory", "2", "test User story2"},
				Child:  []string{"Task", "22", "test Task 22"},
			},
		},
		Blocked: []WorkerWobjReport{
			{
				Parent: []string{"UserStory", "2", "test User story2"},
				Child:  []string{"Task", "23", "test Task 23"},
			},
		},
		Closed: []WorkerWobjReport{},
	},
}

func TestInitListOfWorkerDailyReport(t *testing.T) {
	t.Run("Init test", func(t *testing.T) {
		if len(test_WorkerDailyReports) != 1 {
			t.Errorf("ConvertDailyJsonToHR() = %v, want %v", test_WorkerDailyReport.WorkerID, "WorkerID")
		}
	})
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
