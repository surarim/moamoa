<script>
//filter_req
var filter_text = "";
function filter_req(event)
{
filter_text = document.getElementById("filter").value;
if (event.keyCode == 13)
    {
    document.getElementById("filter_status").innerHTML = "Search starting...";
    var time = performance.now();
    //request
    var csrftoken = '{{ csrf_token }}';
    var req = new XMLHttpRequest();
    req.open('POST', '/filter', true);
    req.setRequestHeader('X-CSRFToken', csrftoken);
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

//server_status_loop
server_status_loop = setTimeout(function tick()
{
//server_status
server_status = document.getElementById("server_status");
server_status_canv = server_status.getContext('2d');
//request
var csrftoken = '{{ csrf_token }}';
var req = new XMLHttpRequest();
req.open('POST', '/server_status', true);
req.setRequestHeader('X-CSRFToken', csrftoken);
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

//default get
window.onload = function()
    {
    //request
    var csrftoken = '{{ csrf_token }}';
    var req = new XMLHttpRequest();
    req.open('POST', '/default', true);
    req.setRequestHeader('X-CSRFToken', csrftoken);
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
