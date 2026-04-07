// 模拟前端时间转换逻辑
const apiTime = 1775199600000; // 后端返回的毫秒时间戳

// useKlineData.ts 的转换逻辑
const numTime = Number(apiTime);
const timeValue = numTime > 100000000000 ? Math.floor(numTime / 1000) : numTime;

console.log('后端返回:', apiTime);
console.log('转换后秒:', timeValue);

// lightweight-charts tickMarkFormatter 逻辑
const date = new Date(timeValue * 1000);
console.log('JavaScript Date:', date);
console.log('.getFullYear():', date.getFullYear());
console.log('getMonth():', date.getMonth()); // 0-11
console.log('getDate():', date.getDate());

const month = String(date.getMonth() + 1).padStart(2, '0');
const day = String(date.getDate()).padStart(2, '0');
console.log('显示日期:', `${month}-${day}`);

// 如果有+2天错误
date.setDate(date.getDate() + 2);
const month2 = String(date.getMonth() + 1).padStart(2, '0');
const day2 = String(date.getDate()).padStart(2, '0');
console.log('如果有+2天:', `${month2}-${day2}`);
