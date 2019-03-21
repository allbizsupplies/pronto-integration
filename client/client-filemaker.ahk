#include %A_SCRIPTDIR%/lib
#include ClientBase.ahk


class Client extends ClientBase {

	enterItems(data) {
		MsgBox % "enterItems"

		for index, line in data.order.items
		{
			; Enter the item line.
			pronto.waitClientStatus(POS_READY_FOR_ITEM)

			; Enter the item code.
			pronto.sendRawOnStatus(line.item_code, POS_READY_FOR_ITEM)
			pronto.sendOnStatus("{Enter}", POS_READY_FOR_ITEM)

			; Enter the item quantity
			if (line.quantity) {
				pronto.sendOnStatus("*{Enter}", POS_READY_FOR_ITEM)
				pronto.sendRawOnStatus(line.quantity, POS_READY_FOR_QUANTITY)
				pronto.sendOnStatus("{Enter}", POS_READY_FOR_QUANTITY)
			}

			; Enter the item price.
			if (line.price) {
				pronto.sendOnStatus("P{Enter}", POS_READY_FOR_ITEM)
				pronto.sendRawOnStatus(line.price, POS_READY_FOR_PRICE)
				pronto.sendOnStatus("{Enter}", POS_READY_FOR_PRICE)
			}

			; Enter the description as a note.
			if (StrLen(line.description) > 0) {
				pronto.sendOnStatus("DN{Enter}", POS_READY_FOR_ITEM)
				pronto.sendRawOnStatus(line.description, POS_READY_FOR_NOTE)
				pronto.sendOnStatus("{Esc}", POS_READY_FOR_NOTE)
				pronto.sendOnStatus("S", POS_SAVE_NOTE)
			}
		}
	}
}


try {
	client := new Client("settings.yml")
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