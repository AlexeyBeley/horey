package main

import ("fmt"
        "errors"
        "os"
        "log"
        )

func main(){
  x := 10.0
  y := fmt.Errorf(" number %g", x)

  fmt.Println(y)
  log.Println(y)
  log.Fatal(y)
  os.Exit(0)

  x1, err := divide(10, 0)
  if err != nil{
  fmt.Println("Found Error", err.Error())
  }

  fmt.Println("HEllo", x1)

}

func divide(x, y int) (int, error) {
if y == 0 {
return 0, errors.New("Divide by zero error")
}
return x/y, nil
}