



// update data
//plotta.UpdateGraph(new data)

// show table
//ShowTable(true or false)

// set y-axis label
//SetAxisYLabel(label)

// set x-axis label
//SetAxisXLabel(label)

const xy = x => t;
const testData = {
  linedatas: [
    {
      id: 'line',
      color: '#55A8DE',
      visible: true,
      dotNum: 1000,
      data = []
    },
  
  ],
  config: {
    font: '',
    legendVisible: true,
    title: {
      location: 'center',
      color: '#666666',
      text: 'Plotta.js'
    },
    grid: {
      type: '',
      visible: true,
      color: '#888888'
    },
    border: {
      type: '',
      visible: true,
      color: '#DDDDDD',
      width: 1
    },
    tics: {
      visible: true,
      color: '#888888',
      value: {
        x: 2,
        y: 2
      }
    },
    axis: {
      t: {
        visible: true,
        label: 'Time',
        color: '#666666',
        location: 'center',
        range: {
          start: -10,
          end: 10
        }
      },
      y: {
        visible: true,
        label: 'Y',
        color: '#666666',
        location: 'center',
        range: {
          start: -50,
          end: 50
        }
      }
    },
    table: {
      visible: true
    }
  }
};