#include %A_SCRIPTDIR%/lib
#include ClientBase.ahk


class Client extends ClientBase {
	enterLineItem(lineItem) {
		base.enterLineItem(lineItem)
	}

	validateLineItems(data) {
		totalPrice := 0

		for index, lineItem in data.order.items
		{
			price := lineItem.price
			quantity := lineItem.quantity

			lineTotal := price * quantity
			totalPrice := totalPrice + lineTotal
    }

		if (totalPrice == 0) {
			throw "The balance for this order is zero."
		}
	}
}


try {
	client := new Client("FileMaker", A_SCRIPTDIR . "/../settings.filemaker.yml")
	client.checkSaleOpen()

	enterShippingAddressDefault := 0
	input := client.getUserInput(enterShippingAddressDefault)
	oid := input.oid
	enterShippingAddress := input.enterShippingAddress

	data := client.getOrderData(oid)

	client.validateLineItems(data)
  client.enterOrderId("FM-" . oid)
	if (enterShippingAddress == 1) {
		data.order.address := { name: data.order.job_name, address_1: data.order.phone_number }
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
