async function refreshStatus(){
  const r = await fetch('/api/status');
  const data = await r.json();
  document.getElementById('status').textContent = `OK @ ${data.time}`;
}
refreshStatus();
setInterval(refreshStatus, 5000);
