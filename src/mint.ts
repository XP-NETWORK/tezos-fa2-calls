import { MichelsonMap, TezosOperationError, TezosToolkit } from "@taquito/taquito";
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
  const collatzContract = await Tezos.contract.at(process.env.COLLATZ_ADDRESS || "")
  const owner = process.env.XPNFT_ADMIN

  const metadata = new MichelsonMap();
  metadata.set("name", char2Bytes("Test"))
  metadata.set("symbol", char2Bytes("Test"))
  metadata.set("decimals", char2Bytes("0"))

  try {
    const tokenId = 0
    const amount = 1
    let op1 = await collatzContract.methods.default(metadata, owner).send({
      fee: 100_000,
      gasLimit: 800_000,
      storageLimit: 60_000,
    })
    console.log(`Waiting for ${op1.hash} to be confirmed...`)
    await op1.confirmation()

    // const op = await Tezos.contract.originate({
    //   code: VIEW_LAMBDA.code,
    //   storage: VIEW_LAMBDA.storage,
    // });
    
    // const lambdaContract = await op.contract();
    // const lambdaContractAddress = lambdaContract.address;

    // const response = await collatzContract.views.balance_of([{
    //   owner: "tz1e4QByQTYQyj98cBiM42hejkMWB2Pg6iXg",
    //   token_id: tokenId
    // }]).read(lambdaContractAddress)
    // const balance: BigNumber = response[0].balance
    // console.log(balance)
  } catch (e) {
    if (e instanceof TezosOperationError) {
      console.error(e.message)
    } else {
      console.error(e)
    }
  }
})();