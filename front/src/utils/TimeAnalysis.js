class TimeAnalysis {
    static processTimeData(data){
        //创建24小时的计数数组
        const hourCounts=new Array(24).fill(0);

        //遍历数据点
        data.forEach(point=>{
            try{
                const date=new Date(point[1]);
                //获取小时并计数
                const hour=date.getHours();
                if(!isNaN(hour)&&hour>=0&&hour<24){
                    hourCounts[hour]++;
                }
            }catch(error){
                console.error('时间解析错误:',error);
            }
        });

        return hourCounts;
    }
}

export default TimeAnalysis;