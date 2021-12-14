import { MichelsonMap, TezosOperationError, TezosToolkit, VIEW_LAMBDA } from "@taquito/taquito";
import { Tzip12Module } from '@taquito/tzip12'
import { InMemorySigner } from "@taquito/signer";
import { char2Bytes } from "@taquito/utils";

require('dotenv').config()

const Tezos = new TezosToolkit(process.env.RPC_URL || "http://localhost:20000");
Tezos.addExtension(new Tzip12Module())

Tezos.setProvider({
  signer: new InMemorySigner(process.env.CREATOR_PK || "edsk3Z2t7t1XimympW62RmUDQeBxn9dw3pQdxxhpAGngmkjiFuXUAj")
});

(async () => {
  const xpnftContract = await Tezos.contract.at(process.env.XPNFT_ADDRESS || "")
  const collatzContract = await Tezos.contract.at(process.env.COLLATZ_ADDRESS || "")

  console.log(`Collatz contract's address: ${collatzContract.address}`)

  const metadata = new MichelsonMap();
  metadata.set("name", char2Bytes("Test"))
  metadata.set("symbol", char2Bytes("Test"))
  metadata.set("decimals", char2Bytes("0"))

  try {
    let op = await xpnftContract.methods.set_administrator(collatzContract.address).send({
      fee: 100_000,
      gasLimit: 800_000,
      storageLimit: 60_000,
    })
    console.log(`Waiting for ${op.hash} to be confirmed...`)
    await op.confirmation()
  } catch (e) {
    if (e instanceof TezosOperationError) {
      console.error(e.message)
    } else {
      console.error(e)
    }
  }
})();