var express = require('express');
const delay = require('delay');
var bodyParser = require('body-parser');

var app = express();


app.use(bodyParser.json()); // for parsing application/json
app.use(bodyParser.urlencoded()); // for parsing application/x-www-form-urlencoded


var produtos = {
    "Avelã": 3000,
    "Banoffee": 2500,
    "Brigadeiro": 2000,
    "Tradicional": 1500,
    "Cha": 2000,
    "Agua": 1000,
    "Refrigerante": 1000,
    "Sanduiche": 10000
} // create an empty array

app.get('/produtos', function (req, res) {
  res.send(produtos)
});


app.post('/pedido', function (req, res) {
  let pedido = req.body.pedido
  console.log(pedido);
  let time = 0;
  if (produtos.hasOwnProperty(pedido)) {
      time = produtos[pedido];
  }
  delay(time, 'a result').then(result => {
      res.json(pedido);
  });
})



app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});
