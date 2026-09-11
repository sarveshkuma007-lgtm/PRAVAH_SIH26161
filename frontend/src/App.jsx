import React, {useMemo, useState} from "react";
import {Activity, AlertTriangle, Bot, Droplets, Gauge, MapPin, Play, RefreshCw, Send, ShieldCheck, Wind} from "lucide-react";
import {AreaChart, Area, ResponsiveContainer, Tooltip, XAxis, YAxis} from "recharts";

const dams = {
  tehri:{name:"Tehri Dam",river:"Bhagirathi River",state:"Uttarakhand, India",water:"818.4",frl:"830.0"},
  sardar_sarovar:{name:"Sardar Sarovar Dam",river:"Narmada River",state:"Gujarat, India",water:"134.2",frl:"138.68"},
  idukki:{name:"Idukki Arch Dam",river:"Periyar River",state:"Kerala, India",water:"720.1",frl:"732.4"}
};
const baseSettlements=[
 {name:"Koteshwar",distance:14,population:"4.2K",risk:"VERY HIGH"},
 {name:"Devprayag",distance:38,population:"12.5K",risk:"HIGH"},
 {name:"Rishikesh",distance:72,population:"102K",risk:"MEDIUM"},
 {name:"Haridwar",distance:94,population:"310K",risk:"MEDIUM"}
];

function App(){
 const [damId,setDamId]=useState("tehri");
 const [width,setWidth]=useState(65),[depth,setDepth]=useState(38),[formation,setFormation]=useState(35);
 const [running,setRunning]=useState(false),[result,setResult]=useState(null);
 const [messages,setMessages]=useState([{role:"bot",text:"PRAVAH Safety Copilot online. I can explain telemetry, simulate a breach, or guide emergency action."}]);
 const [text,setText]=useState("");
 const dam=dams[damId];
 const chartData=useMemo(()=>Array.from({length:11},(_,i)=>({time:i*10,depth:Math.max(0.5,depth*.82*Math.exp(-i*.16)*(width/65))})),[depth,width]);
 const simulate=async()=>{
  setRunning(true);
  try{
   const r=await fetch("http://localhost:8000/api/simulate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({dam_id:damId,breach_width_m:width,breach_depth_m:depth,formation_time_min:formation,failure_mode:"overtopping"})});
   if(r.ok){setResult(await r.json());setRunning(false);return}
  }catch{}
  const peak=Math.round(width*depth*depth*8.4);
  setResult({peak_discharge_cumec:peak,flood_area_km2:Number((width*.42+18.5).toFixed(1)),severity:peak>18000?"CRITICAL":"HIGH",
   settlements:baseSettlements.map((s,i)=>({...s,depth_m:Number(Math.max(.5,depth*.28*Math.exp(-.018*[14,38,72,94][i])*(width/60)).toFixed(2)),arrival_time_min:Number(([14,38,72,94][i]*1.6).toFixed(1))})),
   infrastructure:{hospitals_at_risk:4,schools_at_risk:18,relief_shelters_active:21,bridges_in_red_zone:5,ndrf_teams_deployed:peak>18000?6:2}});
  setRunning(false);
 };
 const ask=async()=>{
  if(!text.trim())return; const q=text;setText("");setMessages(m=>[...m,{role:"user",text:q}]);
  try{const r=await fetch("http://localhost:8000/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:q,active_dam_id:damId})});const d=await r.json();setMessages(m=>[...m,{role:"bot",text:d.reply}]);return}catch{}
  let reply=q.toLowerCase().includes("formula")?"Froehlich: Qp = 0.607 × Vw^0.295 × hw^1.24. Wave celerity: c = √(g × y) + u.":q.toLowerCase().includes("evac")?"Issue a red warning, broadcast SMS/IVR, and move residents to elevated shelters.":"Telemetry analyzed. Use Run Simulation to generate a hazard assessment.";
  setMessages(m=>[...m,{role:"bot",text:reply}]);
 };
 const displaySettlements=result?.settlements||baseSettlements.map((s,i)=>({...s,depth_m:"—",arrival_time_min:"—"}));
 return <div className="app">
  <header className="topbar"><div className="brand"><div className="brand-mark">P</div><div><h1>PRAVAH 360</h1><p>HYDRODYNAMIC DAM SAFETY INTELLIGENCE</p></div></div><div className="live"><Activity size={13} style={{verticalAlign:"-2px"}}/> SYSTEM ONLINE</div></header>
  <div className="layout">
   <aside className="panel">
    <h2>Simulation controls</h2>
    <label className="label">ACTIVE DAM</label>
    <select className="select" value={damId} onChange={e=>{setDamId(e.target.value);setResult(null)}}>{Object.entries(dams).map(([id,d])=><option key={id} value={id}>{d.name}</option>)}</select>
    <div className="label"><span>Breach width</span><span className="value">{width} m</span></div><input className="range" type="range" min="10" max="120" value={width} onChange={e=>setWidth(+e.target.value)}/>
    <div className="label"><span>Breach depth</span><span className="value">{depth} m</span></div><input className="range" type="range" min="5" max="80" value={depth} onChange={e=>setDepth(+e.target.value)}/>
    <div className="label"><span>Formation time</span><span className="value">{formation} min</span></div><input className="range" type="range" min="5" max="120" value={formation} onChange={e=>setFormation(+e.target.value)}/>
    <button className="run" onClick={simulate} disabled={running}><Play size={14} style={{verticalAlign:"-2px"}}/> {running?"CALCULATING...":"RUN BREACH SIMULATION"}</button>
    <button className="ghost" onClick={()=>{setWidth(65);setDepth(38);setFormation(35);setResult(null)}}><RefreshCw size={13} style={{verticalAlign:"-2px"}}/> Reset parameters</button>
    <p className="footer-note">Prototype model for demonstration. Connect validated hydrology and GIS datasets before operational use.</p>
   </aside>
   <main className="center">
    <section className="panel hero"><div className="hero-title"><div><h2>{dam.name}</h2><div className="muted"><MapPin size={12} style={{verticalAlign:"-2px"}}/> {dam.state} · {dam.river}</div></div><ShieldCheck color="#35d5b2" size={22}/></div><div className="chips"><span className="chip">2D WAVE ROUTING</span><span className="chip">FROEHLICH MODEL</span><span className="chip">LIVE TELEMETRY</span></div></section>
    <section className="metrics"><div className="metric"><span className="muted">PEAK DISCHARGE</span><div className="number teal">{result?result.peak_discharge_cumec.toLocaleString():"—"} <small>m³/s</small></div></div><div className="metric"><span className="muted">FLOOD AREA</span><div className="number blue">{result?result.flood_area_km2:"—"} <small>km²</small></div></div><div className="metric"><span className="muted">HAZARD STATUS</span><div className="number amber">{result?.severity||"READY"}</div></div></section>
    <section className="panel"><div className="hero-title"><h2>Flood wave propagation</h2><span className="muted">0–100 min forecast</span></div><div className="chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={chartData}><defs><linearGradient id="wave" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#22c7b0" stopOpacity=".45"/><stop offset="95%" stopColor="#22c7b0" stopOpacity="0"/></linearGradient></defs><XAxis dataKey="time" hide/><YAxis hide/><Tooltip contentStyle={{background:"#0b1b2b",border:"1px solid #284158",fontSize:11}}/><Area type="monotone" dataKey="depth" stroke="#36d6b6" fill="url(#wave)" strokeWidth={2}/></AreaChart></ResponsiveContainer><div className="axis"><span>0 min</span><span>20 min</span><span>40 min</span><span>60 min</span><span>80 min</span><span>100 min</span></div></div><div className="legend"><span><i className="dot" style={{background:"#36d6b6"}}/>Simulated water depth</span><span><i className="dot" style={{background:"#61788e"}}/>Forecast timeline</span></div></section>
    <section className="panel"><div className="hero-title"><h2>Downstream settlement impact</h2><span className="muted">{displaySettlements.length} monitored locations</span></div><table className="table"><thead><tr><th>SETTLEMENT</th><th>DISTANCE</th><th>ARRIVAL</th><th>DEPTH</th><th>RISK</th></tr></thead><tbody>{displaySettlements.map((s,i)=><tr key={s.name}><td>{s.name}</td><td>{s.dist_km??s.distance} km</td><td>{s.arrival_time_min} min</td><td>{s.depth_m} m</td><td><span className={"risk "+(i<2?"high":i===2?"medium":"low")}>{s.risk_level||s.risk}</span></td></tr>)}</tbody></table></section>
   </main>
   <aside className="right">
    <section className="panel"><h2>Live catchment telemetry</h2><div className="weather"><div className="weather-card"><span>TEMPERATURE</span><strong>23.5 °C</strong></div><div className="weather-card"><span>RAINFALL</span><strong>16.8 mm/h</strong></div><div className="weather-card"><span>HUMIDITY</span><strong>85 %</strong></div><div className="weather-card"><span>WIND</span><strong>14.2 km/h</strong></div></div><div className="footer-note"><Droplets size={12} style={{verticalAlign:"-2px"}}/> Cached telemetry preview · connect API for live values</div></section>
    <section className="panel"><h2>Dam status</h2><div className="weather"><div className="weather-card"><span>RESERVOIR LEVEL</span><strong>{dam.water} m</strong></div><div className="weather-card"><span>FULL LEVEL</span><strong>{dam.frl} m</strong></div></div><div className="label"><span>Storage utilization</span><span>{Math.round(Number(dam.water)/Number(dam.frl)*100)}%</span></div><div style={{height:7,background:"#152c40",borderRadius:10}}><div style={{height:"100%",width:`${Number(dam.water)/Number(dam.frl)*100}%`,background:"#2bcab0",borderRadius:10}}/></div></section>
    <section className="panel chat"><h2><Bot size={15} style={{verticalAlign:"-3px"}}/> Safety Copilot</h2><div className="messages">{messages.map((m,i)=><div key={i} className={"msg "+(m.role==="user"?"user":"")}>{m.text}</div>)}</div><div className="chat-input"><input placeholder="Ask about the simulation..." value={text} onChange={e=>setText(e.target.value)} onKeyDown={e=>e.key==="Enter"&&ask()}/><button className="send" onClick={ask}><Send size={14}/></button></div></section>
   </aside>
  </div>
 </div>
}
