package main

import ("net/http"
         "fmt"
         "log"
         "io/ioutil"
         )

func main(){

resp, err := Get("http://example.com/")
   if err != nil {
   log.Fatal("Failed to get:", err)
   }
   fmt.Println(resp)
}

func Get(url string) (_body string, _err error) {
   resp, err := http.Get(url)

   if err != nil {
    log.Fatal(err)
   }

   defer resp.Body.Close()
   if resp.StatusCode != http.StatusOK {
     log.Fatal("HTTP Status code: %d, Status: %s", resp.StatusCode, resp.Status)
   }

   body, err := ioutil.ReadAll(resp.Body)
   if err != nil {
   log.Fatal(err)
   }

   return string(body), nil
}