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

	oid := client.getOrderId()

	data := client.getOrderData(oid)

	client.validateLineItems(data)
  client.enterOrderId("FM-" . oid)
	client.enterLineItems(data)
	client.enterCustomerReference(data)
} catch ex {
	MsgBox % "Error: " . ex
}

ExitApp

; Panic button
^Esc:: ExitApp