#include %A_SCRIPTDIR%/lib
#include ClientBase.ahk


class Client extends ClientBase {
	enterLineItem(lineItem) {
		base.enterLineItem(lineItem)
	}
}


try {
	client := new Client("FileMaker", A_SCRIPTDIR . "/../settings.filemaker.yml")
	client.checkSaleOpen()

	oid := client.getOrderId()

	data := client.getOrderData(oid)

  client.enterOrderId("FM-" . oid)
	client.enterLineItems(data)
	client.enterCustomerReference(data)
} catch ex {
	MsgBox % "Error: " . ex
}

ExitApp

; Panic button
^Esc:: ExitApp