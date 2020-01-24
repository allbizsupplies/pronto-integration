#include JSON.ahk
#include ThinClientController.ahk

; Limit prices and quantities to 4 decimal points.
SetFormat, Float, 0.4


global POS_READY := "Confirm Operator Password"
global POS_READY_FOR_ITEM := "Enter Item Code [HELP], Hotkey or '.' for Options"
global POS_READY_FOR_NOTE := "Press the ESC key to finish (or Save/Cancel)"
global POS_READY_FOR_QUANTITY := ""
global POS_READY_FOR_PRICE := "Enter the item price"
global POS_SAVE_NOTE := "Save your changes"
global POS_CORRECT := "Correct values on the screen"
global POS_READY_FOR_ADDR_LINE := "Enter the delivery address/instr. line"
global POS_READY_FOR_ADDR_POSTCODE := "Enter the postcode for this address"
global POS_READY_FOR_ADDR_PHONE := "Enter the delivery Phone number"
global POS_READY_FOR_ADDR_FAX := "Enter the delivery Fax number"
global POS_READY_FOR_ADDR_DPID := "Enter the delivery point identifier"
global POS_READY_FOR_ADDR_DATE := "Enter the estimated delivery date for this order"
global POS_READY_FOR_CUS_REF := "Enter the customer order no"


class ClientBase {


  __new(window_title, settings_filepath) {
    this.window_title := window_title
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

    this.baseUrl := "http://" . host . ":" . port
  }


  enterOrderId(oid) {
    this.pronto.sendOnStatus("DN{Enter}", POS_READY_FOR_ITEM)
    this.pronto.sendRawOnStatus("Order ID: " . oid, POS_READY_FOR_NOTE)
    this.pronto.sendOnStatus("{Esc}", POS_READY_FOR_NOTE)
    this.pronto.sendOnStatus("S", POS_SAVE_NOTE)
  }


	enterLineItems(data) {
    this.pronto.focusClient()

		for index, lineItem in data.order.items
		{
			this.enterLineItem(lineItem)
    }
	}


  enterCustomerReference(data) {
    if (data.order.reference) {
      reference := data.order.reference

      this.pronto.sendOnStatus("REF{Enter}", POS_READY_FOR_ITEM)
      this.pronto.sendOnStatus(reference, POS_READY_FOR_CUS_REF)
      this.pronto.sendOnStatus("{Enter}", POS_READY_FOR_CUS_REF)
    }
  }


  enterShippingAddress(data) {
    if (data.order.address) {
      address := data.order.address
      
      this.pronto.sendOnStatus("DA{Enter}", POS_READY_FOR_ITEM)
      this.pronto.sendOnStatus("C", POS_CORRECT)

      this.pronto.sendOnStatus(address.name, POS_READY_FOR_ADDR_LINE)
      this.pronto.sendOnStatus("{Enter}", POS_READY_FOR_ADDR_LINE)

      this.pronto.sendOnStatus(address.address_1, POS_READY_FOR_ADDR_LINE)
      this.pronto.sendOnStatus("{Enter}", POS_READY_FOR_ADDR_LINE)

      this.pronto.sendOnStatus(address.address_2, POS_READY_FOR_ADDR_LINE)
      this.pronto.sendOnStatus("{Enter}", POS_READY_FOR_ADDR_LINE)

      this.pronto.sendOnStatus(address.address_3, POS_READY_FOR_ADDR_LINE)
      this.pronto.sendOnStatus("{Enter 4}", POS_READY_FOR_ADDR_LINE)

      this.pronto.sendOnStatus(address.postcode, POS_READY_FOR_ADDR_POSTCODE)
      this.pronto.sendOnStatus("{Enter}", POS_READY_FOR_ADDR_POSTCODE)

      this.pronto.sendOnStatus(address.phone, POS_READY_FOR_ADDR_PHONE)
      this.pronto.sendOnStatus("{F4}", POS_READY_FOR_ADDR_PHONE)
    }
  }


  enterLineItem(lineItem) {
    this.pronto.waitClientStatus(POS_READY_FOR_ITEM)

    ; Enter the item code.
    this.pronto.sendRawOnStatus(lineItem.item_code, POS_READY_FOR_ITEM)
    this.pronto.sendOnStatus("{Enter}", POS_READY_FOR_ITEM)

    ; Enter the item quantity.
    if (lineItem.quantity) {
      this.pronto.sendOnStatus("*{Enter}", POS_READY_FOR_ITEM)
      this.pronto.sendRawOnStatus(lineItem.quantity, POS_READY_FOR_QUANTITY)
      this.pronto.sendOnStatus("{Enter 3}", POS_READY_FOR_QUANTITY)
    }

    ; Enter the item price.
    if (lineItem.price) {
      this.pronto.sendOnStatus("P{Enter}", POS_READY_FOR_ITEM)
      this.pronto.sendRawOnStatus(lineItem.price, POS_READY_FOR_PRICE)
      this.pronto.sendOnStatus("{Enter 3}", POS_READY_FOR_PRICE)
    }

    ; Enter the description as a note.
    if (StrLen(lineItem.description) > 0 || StrLen(lineItem.name) > 0) {
      this.pronto.sendOnStatus("DN{Enter}", POS_READY_FOR_ITEM)

      if (StrLen(lineItem.name) > 0) {
        this.pronto.sendRawOnStatus("Name: " . lineItem.name, POS_READY_FOR_NOTE)
        this.pronto.sendRawOnStatus("`n", POS_READY_FOR_NOTE)
      }

      if (StrLen(lineItem.description) > 0) {
        this.pronto.sendRawOnStatus(lineItem.description, POS_READY_FOR_NOTE)
      }

      this.pronto.sendOnStatus("{Esc}", POS_READY_FOR_NOTE)
      this.pronto.sendOnStatus("S", POS_SAVE_NOTE)
    }
  }


  ; Check that Pronto POS has a sale open.
  checkSaleOpen() {
    this.pronto.focusClient()

    Loop {
      prontoStatus := this.pronto.getClientStatus()

      if (prontoStatus == POS_READY_FOR_ITEM)
        return
      else if (A_Index > 8) {
        throw { What: "You need to have a sale open in POS and ready to enter items." }
      }

      ; Wait 5ms before checking the status again.
      Send, {Enter}
      Sleep, 250
    }
  }


  getOrderId() {
    window_title := this.window_title
    ; Get the order number from the user.
    InputBox, oid , %window_title%, Enter the order number from the jobsheet

    ; Exit if user cancelled or nothing entered.
    if (errorLevel > 0) {
      ExitApp
    }
    else if (oid == "") {
			throw { What: "You didn't enter an order number." }
    }

    return oid
  }

  getUserInput(enterShippingAddressDefault := 0) {
    global orderId
    global enterShippingAddress := enterShippingAddressDefault
    Gui, New, , %window_title%
    Gui, Add, Text,, Enter the order number from the jobsheet
    Gui, Add, Edit, vOrderId
    if (enterShippingAddressDefault == 1)
      Gui, Add, CheckBox, vEnterShippingAddress Checked, Use delivery address from order
    else
      Gui, Add, CheckBox, vEnterShippingAddress, Put job name and phone number in delivery address
    Gui, Add, Button, Default w80 gSubmit, OK
    Gui, Add, Button, w80 x+m yp gCancel, Cancel
    Gui, Show
    GuiOpen := True
    While (GuiOpen) {
      ; Waiting for Submit or Cancel
    }
    Return input

    Submit:
    {
      Gui, Submit
      input := { oid: OrderId, enterShippingAddress: enterShippingAddress }
      Gui, Destroy
      GuiOpen := False
      Return
    }

    Cancel:
    {
      ExitApp
    }
  }


  getOrderData(oid) {
    ; Query the server for the order data.
    httpRequest := ComObjCreate("WinHttp.Winhttprequest.5.1")
    httpRequest.open("GET", this.baseUrl . "/?order=" . oid)
    httpRequest.send()

    data := JSON.decode(httpRequest.responseText)

    if (data.error) {
      MsgBox % "Error: " . data.error
      ExitApp
    }

    return data
  }
}
