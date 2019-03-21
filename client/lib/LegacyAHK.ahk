

; OOP wrapper for AHK functions
class AHK {


  controlGetText(classname, winTitle) {
    ControlGetText, text, %classname%, %winTitle%
    return text
  }


  lowercase(string) {
    StringLower, lowerCaseString, string
    return lowerCaseString
  }


  send(string) {
    Send, %string%
  }


  send_raw(string) {
    SendRaw, %string%
  }


  sleep(duration) {
    Sleep, %duration%
  }
}