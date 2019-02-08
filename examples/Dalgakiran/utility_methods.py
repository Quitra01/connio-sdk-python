
# init()
# getInitialState()
# convertToHours()
# convertToDecimal()    
# makeWriteRequest()
# makeWriteValue()
# fetchWriteRequestList()

#
#
#
def getInit_body():
    return """/**
    Initialize device `state` property with default values
    @value {{ value, unit }} cost of electricity KWh
*/
let settings = Device.fetchModbusSettings();
let state = Device.getEmptyState(value || { 'value': 0, 'unit': 'USD' });
let defaultMaintCosts = { 
    currency_symbol: "$",
    air_filter_change: 0.0,
    oil_change: 0.0,  
    compressor_check: 0.0, 
    oil_filter_change: 0.0, 
    sep_filter_change : 0.0, 
    bearing_lubricator: 0.0     
};

Device.api.setProperty("modbus_settings", {
  value: settings,
  time: new Date().toISOString()
}).
then(p => Device.api.setProperty('maintenanceCostList', {
        value: defaultMaintCosts,
        time: new Date().toISOString()
})).
then(p => Device.getCompressorInfo()).
then(d => {
    // Merge device info into state
    Object.assign(state, d);
    
    Device.api.setProperty('state', {
        value: state,
        time: new Date().toISOString()
    }).then(property => done(null, property.value));
});
"""

#
#
#
def getEmptyState_body():
    return """/**
    Creates an empty state for this device
    @value {{ value, unit }} cost of electricity KWh
*/
return {        
    costOfkWh: {
        value: value.value,
        unit: value.unit,
    },
    warnings: { last: [], asOf: "2019-01-01T00:00:00Z", total: [ 0, 0, 0, 0 ] },
    alarms: { last: [], asOf: "2019-01-01T00:00:00Z", total: [ 0, 0, 0, 0 ] },
    pressure: { value: 0, unit: "bar", average: [ 0, 0, 0, 0 ] },    
    temperature: { value: 0, unit: "°C", average: [ 0, 0, 0, 0 ] },
    maintenance: { upcoming: [
                { maintenance: "Bearing Lubrication", cost: 0, hours: 0, days: 0 },
                { maintenance: "Air Filter Change", cost: 0, hours: 0, days: 0 },
                { maintenance: "Oil Filter Change", cost: 0, hours: 0, days: 0 },
                { maintenance: "Oil Change", cost: 0, hours: 0, days: 0 },
                { maintenance: "Seperator Filter Change", cost: 0, hours: 0, days: 0 },
                { maintenance: "Compressor Check", cost: 0, hours: 0, days: 0 }
            ]
    },
    stoppages: { planned: [ 0, 0, 0, 0 ], unplanned: [ 0, 0, 0, 0 ], powercut: [ 0, 0, 0, 0 ] },
    loadRatio: { average: [ 0, 0, 0, 0 ], current: 0, unit: "%" },
    energy: { value: [ 0, 0, 0, 0 ], unit: "kWh" },        
    unplannedStoppageHours: [ 0, 0, 0, 0 ],
    loadRunningHours: [ 0, 0, 0, 0 ],        
    power: { value: [ 0, 0, 0, 0 ], unit: "kW" },                
    costOfRunning: { value: [ 0, 0, 0, 0 ], unit: "USD"},
    idleRunningHours: [ 0, 0, 0, 0 ],
    plannedStoppageHours: [ 0, 0, 0, 0 ],
    unplannedStoppageHours: [ 0, 0, 0, 0 ],
    loadRunningHours: [ 0, 0, 0, 0 ],
    totalHours: { last: 0, asOf: "2019-01-01T00:00:00.000Z", average: [ 0, 0, 0, 0 ] },
    totalLoadHours: { last: 0, asOf: "2019-01-01T00:00:00.000Z", average: [ 0, 0, 0, 0 ] },
    oee: { availability: 0, performance: [ 0, 0, 0, 0 ], quality: [ 0, 0, 0, 0 ], average: [ 0, 0, 0, 0 ], unit: '%' },
    mtbf: { average: [ 0, 0, 0, 0 ], unit: 'h' },
    mttr: { average: [ 0, 0, 0, 0 ], unit: 'h' },
    hasInverter: false, 
    motorSpeed: { current: 0, average: [ 0, 0, 0, 0 ], unit: 'RPM' },
    motorFrequency: { current: 0, average: [ 0, 0, 0, 0 ], unit: 'Hz' },
    motorCurrent: { current: 0, average: [ 0, 0, 0, 0 ], unit: 'A' },
    status: {
        code: 0,
    },
};
"""

#
#
#
def convertToHours_body(): 
    return """/**
    Converts given Logika hour representation to hours
    @value [word1, word2] 
*/
function convert(word1, word2) {
    var byte1 = (word2 & 255) << 24;
    var byte2 = (word2 >>> 8) << 16;
    var byte3 = (word1 & 255) << 8;
    var byte4 = (word1 >>> 8);
    
    // calculate and divide by 60 to convert minutes into hours        
    return (byte1 | byte2 | byte3 | byte4) / 60.0;
};
done(null, convert(value[0], value[1]));
"""

#
#
#
def convertToDec_body():
    return """/** 
    Converts given big-endien byte array to decimal values
    @value: {{ values: [b1, b2, b3, ..], default: x }}
*/

let values = value.values;
let defaultValue = value.default;

if (!Array.isArray(values) || values.length == 0) return defaultValue;

let result = 0;
let offset = 0;
for (var i = values.length - 1; i >= 0; i--) {
    result |= values[i] << (offset * 8);
    offset += 1;
}
return result;
"""

#
#
#
def makeWriteRequest_body():
    return """/**
    @param value.tagKey   (e.g. "WP")
    @param value.x        (e.g. 1 for WP1)
    @param value.setValue (e.g. 26.8)
    @param value.byteCount(default 2)
*/
let params = Device.fetchWriteRequest(value.tagKey);
let byteCount = value.byteCount || 2;

let tag_address;
if (value.x > params.max || value.x < params.min) { 
    throw "Invalid tag index "+ value.tagKey + "("+ value.x.toString() +") should be between " + params.min.toString() + "-" + params.max.toString();
}
else {
    tag_address = parseInt(params.offset, 16) + (value.x - params.min);
}

let multip = params.multiplier || 10;

let tagValue = Device.makeWriteValue({ value: (value.setValue * multip), byteCount: byteCount });

return { writeRequest: "w," + tagValue.join(':') + "," + byteCount.toString() + ",0,1,0x" + tag_address.toString(16),
        readRequest: params.rcmd
        };"""

#
#
#
def makeWriteValue_body():
    return """/**
    @value {{ value, byteCount }}
*/
function convert(v, byteCount) {
    let hex = v.toString(16);
    if (hex.length % 2) hex = '0' + hex;
    
    // group chars by 2
    let hexArr = hex.match(/(.{2})/g);
    for (let x = hexArr.length; x < byteCount; x++) {
        hexArr.unshift('00');
    }
    
    return hexArr.map(x => x.split('').reduce((result, ch) => result * 16 + '0123456789abcdefgh'.indexOf(ch), 0));
}
return convert(value.value, value.byteCount);"""

#
#
#
def getCompressorInfo_body():
    return """/**

*/
const serNumPropName        = "cfgSerialNumber";
const modelPropName         = "cfgLogikaModel";
const fwVerPropName         = "cfgLogikaFwVersion";
const compStatePropName     = "compressorState";
const connStatusPropName    = "connectionStatus";
const activityPropName      = "active";
const warrantyEndPropName   = "warrantyExpiresIn";

async function f() {    
    if (Device.customIds && !Device.customIds.sn) {
        Device.customIds.sn = await Device.api.getProperty(serNumPropName).then(p=>p.value || "-");
    }
    
    let logika_model = await Device.api.getProperty(modelPropName).then(p=>p.value  || "-");
    let logika_release = await Device.api.getProperty(fwVerPropName).then(p=>p.value  || "-");
    
    let status = await Device.api.getProperty(compStatePropName).then(p=>p.value  || "-");
    let connection = await Device.api.getProperty(connStatusPropName).then(p=>p.value  || "-");
    let active = await Device.api.getProperty(activityPropName).then(p=>p.value  || "-");
    
    let connectivity = "offline";
    if (connection === "online" && active == "active") {
        connectivity = "online-active";
    }
    else if (connection === "online") {
        connectivity = "online-inactive";
    }
    
    let warrantyInfoProp = await Device.api.getProperty(warrantyEndPropName);
    let timeToWarranty = warrantyInfoProp.value || 0;
    
    // In case that we use a counter to decrement the warranty time
    if (timeToWarranty < 0) {
        timeToWarranty = 0;
    }
    
    let device = {
        id: Device.id,
        name: Device.name,
        friendlyName: Device.friendlyName,
        customIds: Device.customIds || { sn: await Device.api.getProperty(serNumPropName).then(p=>p.value || "-") },
        logikaModel: logika_model,
        logikaRelease: logika_release,
        connectivity: connectivity,
        status: status,
        warrantyEnd: timeToWarranty + " " + warrantyInfoProp.meta.measurement.unit.symbol,
    };
    return device;
}
return Promise.resolve(f());
"""

#
#
#
def getDashboardParallel_body():
    return """/**

*/
const PRESSURE_PROPERTY = 'workingPressure';
const TEMPERATURE_PROPERTY = 'screwTemperature';
const STATE_PROPERTY = 'state';

async function main(context) {
    Object.assign(context, {
        costOfkWh: value,
    });

    // Acquire temperature and pressure values in parallel
    let [pressureProp, temperatureProp] = await Promise.all([
       Device.api.getProperty(PRESSURE_PROPERTY),
       Device.api.getProperty(TEMPERATURE_PROPERTY)
    ]);

    context.pressure.value = pressureProp.value || 0;
    context.pressure.unit = pressureProp.meta.measurement && pressureProp.meta.measurement.unit && pressureProp.meta.measurement.unit.symbol;

    if (pressureProp.meta.boundaries) {
        context.pressure.range = {
            min: pressureProp.meta.boundaries.min,
            max: pressureProp.meta.boundaries.max,
        };
    }
    
    context.temperature.value = temperatureProp.value || 0;
    context.temperature.unit = temperatureProp.meta.measurement && temperatureProp.meta.measurement.unit && temperatureProp.meta.measurement.unit.symbol;

    if (temperatureProp.meta.boundaries) {
        context.temperature.range = {
            min: temperatureProp.meta.boundaries.min,
            max: temperatureProp.meta.boundaries.max,
        };
    }

    // Call the methods below in parallel.
    // These methods do not have any dependence on other method output.
    let results = await Promise.all([
        Device.getCompressorInfo(),
        Device.queryWarningAlarmSummary(context),
    //     Device.getTimeToMaintenance(context),
    //     Device.hasInverter(context),
    ]);
    
    // Merge results into context
    results.forEach(result => Object.assign(context, result));

    return context;
};

Device.api.getProperty(STATE_PROPERTY)
 .then(property => property.value || Device.getEmptyState())
 .then(main)
 .then(context => Device.api.setProperty(STATE_PROPERTY, { value: context, time: new Date().toISOString() }))
 .then(property => done(null, property.value));
"""

def getLatestValues_body():
    return """/**

*/
const PRESSURE_PROPERTY = 'workingPressure';
const TEMPERATURE_PROPERTY = 'screwTemperature';

async function main() {
    let [pressureProp, temperatureProp] = await Promise.all([
      Device.api.getProperty(PRESSURE_PROPERTY),
      Device.api.getProperty(TEMPERATURE_PROPERTY)
    ]);
    
    const result = {
        pressure: pressureProp.value || 0,
        temperature: temperatureProp.value || 0,
    };

    return done(null, result);
};

main();
"""