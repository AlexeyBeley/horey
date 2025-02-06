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


func TestConvertDailyJsonToHR(t *testing.T) {
  tests:=struct {
                name     string
                filename string
                want    WorkerDailyReport
                wantErr  bool
        }{
                {
                        name:     "Valid JSON",
                        filename: "test_data.json", // Create this test file
                        want: WorkerDailyReport{
                                {WorkerID: "horey", New: {{"child": {"1", "2", "3"}, "parent":{"4","5","6"}}}, Active: {}, Blocked: {}, Closed: {}},
                        },
                        wantErr: false,
                },
                {
                        name:     "Invalid JSON",
                        filename: "invalid_data.json", // Create this file with invalid JSON
                        want:     nil,
                        wantErr:  true,
                },
                {
                        name:     "File Not Found",
                        filename: "nonexistent.json",
                        want:     nil,
                        wantErr:  true,
                },
        }

   for _, tt := range tests {
     t.Run(tt.name, func(t *testing.T){
     got, err := ConvertDailyJsonToHR(tt.filename, "dst_file_path")

     if (err != nil) != tt.wantErr{
       t.Errorf("readItemsFromFile() error = %v, wantErr %v", err, tt.wantErr)
       return
     }

     if !reflect.DeepEqual(got, tt.want) {
      t.Errorf("ConvertDailyJsonToHR() = %v, want %v", got, tt.want)
     }
     })
   }
 }