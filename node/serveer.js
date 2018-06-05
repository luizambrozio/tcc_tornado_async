var express = require('express');
const delay = require('delay');
var bodyParser = require('body-parser');

var app = express();


app.use(bodyParser.json()); // for parsing application/json
app.use(bodyParser.urlencoded()); // for parsing application/x-www-form-urlencoded


// {
// Avelã = 3s
// Banoffee = 2.5s
// Brigadeiro = 2s
// tradicional = 1.5s
// cha = 2s
// agua = 1s
// refri = 1s
// sanduiche = 10s
// }

var produtos = [
  {key:"Avelã", value: 3000},
  {key:"Banoffee", value:2500},
  {key:"Brigadeiro", value:2000},
  {key:"tradicional", value:1500},
  {key:"cha", value:2000},
  {key:"agua", value:1000},
  {key:"refrigerante", value:1000},
  {key:"sanduiche", value:10000}
]; // create an empty array

app.get('/produtos', function (req, res) {
  res.send(produtos)
});


app.post('/pedido', function (req, res) {
  let pedidos = req.body.pedido
  let time = 0

  pedidos.forEach(element => {
    produtos.forEach(e => {
      if (e.key === element) {
          if (e.value > time) {
            time =e.value
          }        
      }
    })
  });

  delay(time, 'a result')
    .then(result => {
      res.json(pedidos);
    }); 
});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});

