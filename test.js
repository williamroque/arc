function addToDate(date, i) {
    const MONTHS = 'Jan|Fev|Mar|Abr|Mai|Jun|Jul|Ago|Set|Out|Nov|Dez'.split('|').map(m => m.toLowerCase());
    let [month, year] = date.split('/');

    const monthIndex = MONTHS.indexOf(month.toLowerCase());

    year |= 0;

    if (i < 0) {
        year -= Math.ceil(-((monthIndex + i) / 12));
    } else {
        year += (monthIndex + i) / 12 | 0;
    }

    month = MONTHS[(12 + monthIndex + i % 12) % 12];

    return `${month}/${year}`;
}

for (let i = -50; i < 31; i++) {
    console.log(i, addToDate('set/2019', i));
}
