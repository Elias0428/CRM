var options = {
    series: [
        {
            name: "ObamaCare",
            data: obamacareSales.map(Number),
        },
        {
            name: "Supp",
            data: suppSales.map(Number),
        },
    ],
    chart: {
        type: 'bar',
        height: 350,
        stacked: true,
        toolbar: {
            show: true
        },
        zoom: {
            enabled: true
        }
    },
    responsive: [{
        breakpoint: 480,
        options: {
            legend: {
                position: 'bottom',
                offsetX: -10,
                offsetY: 0
            }
        }
    }],
    plotOptions: {
        bar: {
            horizontal: false,
            borderRadius: 10,
            borderRadiusApplication: 'end',
            borderRadiusWhenStacked: 'last',
        }
    },
    dataLabels: {
        enabled: true,
        formatter: function (val, opts) {
            return val; // Mostrar valores dentro de cada segmento
        },
        style: {
            fontSize: '14px',
            fontWeight: 'bold',
            colors: ['#000']
        },
        offsetY: -5
    },
    annotations: {
        points: agents.map((agent, index) => {
            let total = obamacareSales[index] + suppSales[index];
            return {
                x: agent,  // 🔥 Ahora usamos el nombre del agente en lugar del índice
                y: total,  // 📌 Posicionamos el total en la parte superior de la barra
                marker: {
                    size: 0 // Ocultamos el marcador para evitar que aparezca un círculo negro
                },
                label: {
                    text: total.toString(),
                    style: {
                        fontSize: '14px',
                        fontWeight: 'bold',
                        background: '#fff',
                        color: '#000'
                    },
                    offsetY: -10
                }
            };
        })
    },
    xaxis: {
        categories: agents,
    },
    legend: {
        position: 'right',
        offsetY: 40
    },
    fill: {
        opacity: 1
    }
};

var chart = new ApexCharts(document.querySelector("#mainChart"), options);
chart.render();
