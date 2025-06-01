// Flatpickr

var f1 = flatpickr(document.getElementById('basicFlatpickr'));
var f22 = flatpickr(document.getElementById('basicFlatpickr22'));
var f23 = flatpickr(document.getElementById('basicFlatpickr23'));
var f24 = flatpickr(document.getElementById('basicFlatpickr24'));
var f12 = flatpickr(document.getElementById('basicFlatpickr2'));
var f2 = flatpickr(document.getElementById('dateTimeFlatpickr'), {
    enableTime: true,
    dateFormat: "Y-m-d H:i",
});
var f3 = flatpickr(document.getElementById('rangeCalendarFlatpickr'), {
    mode: "range",
});
var f4 = flatpickr(document.getElementById('timeFlatpickr'), {
    enableTime: true,
    noCalendar: true,
    dateFormat: "H:i",
    defaultDate: "13:45"
});