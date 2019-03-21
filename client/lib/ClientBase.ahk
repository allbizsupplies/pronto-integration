#include JSON.ahk
#include ThinClientController.ahk


; Limit prices and quantities to 4 decimal points.
SetFormat, Float, 0.4


class ClientBase {

  POS_READY := "Confirm Operator Password"
  POS_READY_FOR_ITEM := "Enter Item Code [HELP], Hotkey or '.' for Options"
  POS_READY_FOR_NOTE := "Press the ESC key to finish (or Save/Cancel)"
  POS_READY_FOR_QUANTITY := ""
  POS_READY_FOR_PRICE := "Enter the item price"
  POS_SAVE_NOTE := "Save your changes"


  __new(settings_filepath) {
    this.pronto := new ThinClientController()

    ; Get the host and port from the settings file.
    Loop, Read, %settings_filepath%
    {
        option := StrSplit(A_LoopReadLine , ":", " ")

        if (option[1] == "host")
            host := option[2]
        else if (option[1] == "port")
            port := option[2]
    }

    if (host == "" || port == "")
      throw "Unable to get server settings."

    this.url := "http://" . host . ":" . port . "/?order=" . oid
  }


  ; Check that Pronto POS has a sale open.
  checkSaleOpen() {
    this.pronto.focusClient()

    Loop {
      prontoStatus := pronto.getClientStatus()
      if (prontoStatus == POS_READY_FOR_ITEM)
        break
      else if (A_Index > 8) {
        throw "You need to have a sale open in POS and ready to enter items."
      }

      ; Wait 5ms before checking the status again.
      Send, {Enter}
      Sleep, 250
    }
  }


  getOrderId() {
    ; Get the order number from the user.
    InputBox, oid , "ENP", "Enter the order number from the jobsheet"

    ; Exit if user cancelled or nothing entered.
    if (errorLevel > 0) {
      ExitApp
    }
    else if (oid == "") {
      throw "You didn't enter an order number."
    }

    return oid
  }


  getOrderData() {
    ; Query the server for the order data.
    httpRequest := ComObjCreate("WinHttp.Winhttprequest.5.1")
    httpRequest.open("GET", this.url)
    httpRequest.send()
    data := JSON.decode(httpRequest.responseText)
  }
}