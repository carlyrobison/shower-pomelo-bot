const express = require('express');
const app     = express();
const PORT    = process.env.PORT || 3000;
const server  = require('http').createServer(app);
const io      = require('socket.io')(server);


io.on('connection', function (socket) {
  console.log("New socket client connection: ", socket.id);
});

// --------------------------------------------------------
// EXPRESS STUFF
// --------------------------------------------------------
// tell our app where to serve our static files
app.use(express.static('public'));

// --------------------------------------------------------
// define a route - what happens when people visit /
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

// --------------------------------------------------------
// tell our app where to listen for connections
server.listen(PORT, () => {
  console.log('Listening on PORT ' + PORT);
});
