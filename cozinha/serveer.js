var express = require('express');
const delay = require('delay');
var bodyParser = require('body-parser');

var app = express();


app.use(bodyParser.json()); // for parsing application/json
app.use(bodyParser.urlencoded()); // for parsing application/x-www-form-urlencoded


var produtos = [
  {key:"Avelã", value: 3000},
  {key:"Banoffee", value:2500},
  {key:"Brigadeiro", value:2000},
  {key:"Tradicional", value:1500},
  {key:"Cha", value:2000},
  {key:"Agua", value:1000},
  {key:"Refrigerante", value:1000},
  {key:"Sanduiche", value:10000}
]; // create an empty array

app.get('/produtos', function (req, res) {
  res.send(produtos)
});


app.post('/pedido', function (req, res) {
  let pedido = req.body.pedido
  console.log(pedido);
  produtos.forEach(e => {
    if(e.key == pedido){
      delay(e.value, 'a result')
      .then(result => {
        res.json(pedido);
      });
    }
  });
})



app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});
