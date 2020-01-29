#include %A_SCRIPTDIR%/lib
#include ClientBase.ahk


class Client extends ClientBase {
	enterLineItem(lineItem) {
		base.enterLineItem(lineItem)
	}
}


try {
	client := new Client("Web Orders", A_SCRIPTDIR . "/../settings.editandprint.yml")
	client.checkSaleOpen()

	enterShippingAddressDefault := 1
	input := client.getUserInput(enterShippingAddressDefault)
	oid := input.oid
	enterShippingAddress := input.enterShippingAddress

	data := client.getOrderData(oid)

	client.validateLineItems(data)
  client.enterOrderId("WEB-" . oid)
	if (enterShippingAddress == 1) {
		client.enterShippingAddress(data)
	}
	client.enterCustomerReference(data)
	client.enterLineItems(data)
} catch e {
	MsgBox % "Error: " . e.What . "`nLine: " . e.Line . "`nExtra: " . e.Extra
}

ExitApp

; Panic button
^Esc:: ExitApp