#include %A_SCRIPTDIR%/lib
#include ClientBase.ahk


class Client extends ClientBase {
	enterLineItem(lineItem) {
		base.enterLineItem(lineItem)

		for index, option in lineItem.options
		{
			if (option.value != "No") {
				description := option.key . ":`n  " . option.value

				this.pronto.sendOnStatus("DN{Enter}", POS_READY_FOR_ITEM)
				this.pronto.sendRawOnStatus(description, POS_READY_FOR_NOTE)
				this.pronto.sendOnStatus("{Esc}", POS_READY_FOR_NOTE)
				this.pronto.sendOnStatus("S", POS_SAVE_NOTE)
			}
    }
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