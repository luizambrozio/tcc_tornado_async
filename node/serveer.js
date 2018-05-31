var express = require('express');
const delay = require('delay');

var app = express();

app.get('/2s', function (req, res) {
  delay(2000, 'a result')
    .then(result => {
        console.log('2000');
        res.send('val');
    });

});

app.get('/5s', function (req, res) {
  delay(5000, 'a result')
    .then(result => {
        console.log('5000');
        res.send('val');
    });

});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});
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
