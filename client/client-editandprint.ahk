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

	oid := client.getOrderId()

	data := client.getOrderData(oid)
  data.order.reference := oid

  client.enterOrderId("WEB-" . oid)
	client.enterShippingAddress(data)
	client.enterCustomerReference(data)
	client.enterLineItems(data)
} catch ex {
	MsgBox % "Error: " . ex
}

ExitApp

; Panic button
^Esc:: ExitApp