document.addEventListener("DOMContentLoaded", () => {
  const medForm = document.getElementById("medicineForm");
  const medList = document.getElementById("medicineList");

  medForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    const name = document.getElementById("name").value;
    const dose = document.getElementById("dose").value;
    const time = document.getElementById("time").value;

    const li = document.createElement("li");
    li.textContent = `${name} - ${dose} at ${time}`;
    medList.appendChild(li);

    scheduleAlarm(name, dose, time);
  });

  const billForm = document.getElementById("billForm");
  const billOutput = document.getElementById("billOutput");

  billForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(billForm);
    const res = await fetch("/upload_bill", { method: "POST", body: formData });
    const data = await res.json();
    billOutput.textContent = JSON.stringify(data, null, 2);
  });
});

function scheduleAlarm(name, dose, time) {
  const [hh, mm] = time.split(":");
  const now = new Date();
  const target = new Date();
  target.setHours(hh, mm, 0, 0);
  if (target < now) target.setDate(target.getDate() + 1);
  const delay = target - now;

  setTimeout(() => {
    notify(`${name} - ${dose || ""}`);
  }, delay);
}

function notify(text) {
  if (Notification.permission === "default") Notification.requestPermission();
  if (Notification.permission === "granted") {
    new Notification("Medicine Reminder", { body: text });
  }
  alert(text);
  const audio = new Audio("/static/alarm.mp3");
  audio.play();
}
// target: document.querySelector('.progress-bar')
function setProgress(p){ // p = 0..100
  const bar = document.querySelector('.progress-bar');
  const total = 100; // path length simulated by dasharray percentages
  bar.setAttribute('stroke-dasharray', `${p} ${total - p}`);
}
