<script>
// Function of filter search and output to the form
// Функция поиска по фильтру и вывода в форму
function filter_req(event)
{
filter_text = document.getElementById("filter").value;
if (event.keyCode == 13)
    {
    document.getElementById("filter_status").innerHTML = "Search starting...";
    var time = performance.now();
    var req = new XMLHttpRequest();
    req.open('POST', '/filter', true);
    req.onreadystatechange = function()
            {
	    if (req.readyState == XMLHttpRequest.DONE && req.status == 200)
                {
                if (req.responseText != "")
                    { document.getElementById("list").innerHTML = req.responseText; }
                    else { document.getElementById("list").innerHTML = "Rows not found"; }
                time = (performance.now() - time)/1000;
                document.getElementById("filter_status").innerHTML = "Search completed, time: "+time.toFixed(3)+" sec";
                }
            }
    req.send(filter_text);
    };
};

// Function of getting server status (process of reading the port and writing to the database)
// Функция получения статуса сервера (процесс чтения порта и записи в базу)
server_status_loop = setTimeout(function tick()
{
server_status = document.getElementById("server_status");
server_status_canv = server_status.getContext('2d');
var req = new XMLHttpRequest();
req.open('POST', '/server_status', true);
req.onreadystatechange = function()
    {
    server_status_canv.fillStyle = "rgb(0,0,0)";
    server_status_canv.fillRect(0,0,server_status.width,server_status.height);
    if (req.readyState == XMLHttpRequest.DONE && req.responseText == 'ok')
        { server_status_canv.fillStyle = "rgb(10,250,10)"; }
    server_status_canv.fillRect(1,1,server_status.width-2,server_status.height-2);
    }
req.send();
//
server_status_loop = setTimeout(tick, 10000);
}, 10000);

// Function of reading the database when the form starts
// Функция чтения базы при старте формы
window.onload = function()
    {
    var req = new XMLHttpRequest();
    req.open('POST', '/default', true);
    req.onreadystatechange = function()
            {
	    if (req.readyState == XMLHttpRequest.DONE && req.status == 200)
                {
                if (req.responseText != "")
                    { document.getElementById("list").innerHTML = req.responseText; }
                    else { document.getElementById("list").innerHTML = "Rows not found"; }
                }
            }
    req.send();
    };
</script>
