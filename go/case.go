package main
import ("fmt"; "time")

var channelOut = make(chan  int)
var channelIn = make(chan  int)
func main (){

go func (channelOut chan int) {
 for x := range 10000000{
 fmt.Println("We could read from channelIn", x)
}
}(channelOut)

doStuff(channelOut, channelIn)
}




func doStuff(channelOut, channelIn chan int) {
 select {
 case channelOut <- 42:
 fmt.Println("We could write to channelOut!")
 case x := <- channelIn:
 fmt.Println("We could read from channelIn", x)
 case <-time.After(time.Second * 1):
 fmt.Println("timeout")
 }
}

