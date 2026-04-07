// 检查 IndexedDB 缓存
const request = indexedDB.open('myquant-kline', 1);

request.onsuccess = async (event) => {
  const db = event.target.result;
  const tx = db.transaction(['kline'], 'readonly');
  const store = tx.objectStore('kline');
  
  // 获取 000001.SZ 的所有缓存
  const getAllRequest = store.getAll();
  
  getAllRequest.onsuccess = (e) => {
    const allData = e.target.result;
    const szData = allData.filter(d => d.symbol === '000001.SZ' && d.period === '1d');
    
    console.log('IndexedDB 缓存的平安银行日线数据:');
    szData.forEach(d => {
      console.log('键:', d.key);
      console.log('最后更新:', new Date(d.updatedAt).toLocaleString());
      console.log('数据量:', d.data.length);
      console.log('最新日期:', new Date(d.data[d.data.length-1].time * 1000).toLocaleDateString());
      console.log('---');
    });
    
    db.close();
  };
};

request.onerror = (e) => {
  console.error('打开 IndexedDB 失败:', e);
};
