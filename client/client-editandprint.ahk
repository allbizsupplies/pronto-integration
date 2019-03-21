#include %A_SCRIPTDIR%/lib
#include ClientBase.ahk


class Client extends ClientBase {
	enterItems(data) {
		MsgBox % "Enter items"
	}
}


try {
	client = new Client("settings.yml")
	client.checkSaleOpen()
	oid := client.getOrderId()
	data := client.getOrderData(oid)
	client.enterItems(data)
} catch ex {
	MsgBox % "Error: " . ex
}

ExitApp

; Panic button
^Esc:: ExitApp