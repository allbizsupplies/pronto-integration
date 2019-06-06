#include %A_SCRIPTDIR%/lib
#include ClientBase.ahk


class Client extends ClientBase {
	
}


try {
	client := new Client("../settings.filemaker.yml")
	client.checkSaleOpen()

	oid := client.getOrderId()

	data := client.getOrderData(oid)

  client.enterOrderId("FM-" . oid)
	client.enterShippingAddress(data)
	client.enterLineItems(data)
	client.enterCustomerReference(data)
} catch ex {
	MsgBox % "Error: " . ex
}

ExitApp

; Panic button
^Esc:: ExitApp