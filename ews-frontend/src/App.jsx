// // App.jsx
// import { useState } from 'react'
// import axios from 'axios'
// import './App.css'

// function App() {
//   // 1. STATE (Data Storage)
//   const [formData, setFormData] = useState({
//     person_age: '',
//     person_income: '',
//     person_home_ownership: '',
//     person_emp_length: '',
//     loan_intent: '',
//     loan_grade: '',
//     loan_amnt: '',
//     loan_int_rate: '',
//     loan_percent_income: '',
//     cb_person_default_on_file: '',
//     cb_person_cred_hist_length: ''
//   })
//   const [result, setResult] = useState(null)

//   // 2. LOGIC (Math and Event Handlers)
//   const gradeToInterestRate = {
//     A: 6.5,
//     B: 9.5,
//     C: 13.5,
//     D: 16.5,
//     E: 19.5,
//     F: 22.5,
//     G: 25.5
//   };

//   const handleChange = (e) => {
//     const { name, value } = e.target;
//     let updatedFormData = { ...formData, [name]: value };

//     // If Loan Grade changes, auto-fill the Interest Rate
//     if (name === 'loan_grade' && value !== '') {
//       updatedFormData.loan_int_rate = gradeToInterestRate[value];
//     }
//     setFormData(updatedFormData);
//   }

//   const handleSubmit = async (e) => {
//     e.preventDefault()
    
//     // Convert strings to numbers for the Machine Learning model
//     const payload = {
//     person_age: Number(formData.person_age),
//     person_income: Number(formData.person_income),
//     person_home_ownership: formData.person_home_ownership, // Text (e.g., 'RENT')
//     person_emp_length: Number(formData.person_emp_length),
//     loan_intent: formData.loan_intent,                     // Text (e.g., 'EDUCATION')
//     loan_grade: formData.loan_grade,                       // Text (e.g., 'A')
//     loan_amnt: Number(formData.loan_amnt),
//     loan_int_rate: Number(formData.loan_int_rate),
//     loan_percent_income: Number(formData.loan_percent_income),
//     cb_person_default_on_file: formData.cb_person_default_on_file, // Text ('Y' or 'N')
//     cb_person_cred_hist_length: Number(formData.cb_person_cred_hist_length)
//   }
    

//     try {
//       // Wiring the frontend to your local Django API
//       const response = await axios.post('/api/predict/', payload)
//       setResult(response.data)
//     }  catch (error) {
//       if (error.response) {
//         // Django rejected it! Let's see exactly what Django said:
//         console.error("Django says:", error.response.data)
//         alert("Django Error: " + JSON.stringify(error.response.data))
//       } else {
//         console.error("Network Error:", error)
//         alert("Failed to connect to the API. Is Django running?")
//       }
//     }
//   }
    
    
//   //   catch (error) {
//   //     console.error("API Error:", error)
//   //     alert("Failed to connect to the API. Is Django running?")
//   //   }
//   // }

//   return (
//     <div className="form-container">
//       <h2>EWS AI Portal</h2>
      
//       <form onSubmit={handleSubmit}>
//         <div className="input-group">
//           <label>Applicant Age</label>
//           <input type="number" name="person_age" required onChange={handleChange} placeholder="e.g., 28" />
//         </div>
        
//         <div className="input-group">
//           <label>Annual Income ($)</label>
//           <input type="number" name="person_income" required onChange={handleChange} placeholder="e.g., 65000" />
//         </div>

//         <div className="input-group">
//           <label>Requested Loan Amount ($)</label>
//           <input type="number" name="loan_amnt" required onChange={handleChange} placeholder="e.g., 15000" />
//         </div>
        
//         <div className="input-group">
//           <label>Employment Length (Years)</label>
//           <input type="number" name="person_emp_length" required onChange={handleChange} />
//         </div>

//         <div className="input-group">
//           <label>Interest Rate (%)</label>
//           <input type="number" step="0.01" name="loan_int_rate" required onChange={handleChange} />
//         </div>

//         <div className="input-group">
//           <label>Loan Percent of Income (e.g., 0.20)</label>
//           <input type="number" step="0.01" name="loan_percent_income" required onChange={handleChange} />
//         </div>

//         <div className="input-group">
//           <label>Credit History Length (Years)</label>
//           <input type="number" name="cb_person_cred_hist_length" required onChange={handleChange} />
//         </div>

//         <div className="input-group">
//           <label>Home Ownership</label>
//           <select name="person_home_ownership" required onChange={handleChange}>
//             <option value="">Select...</option>
//             <option value="RENT">Rent</option>
//             <option value="OWN">Own</option>
//             <option value="MORTGAGE">Mortgage</option>
//             <option value="OTHER">Other</option>
//           </select>
//         </div>

//         <div className="input-group">
//           <label>Loan Intent</label>
//           <select name="loan_intent" required onChange={handleChange}>
//             <option value="">Select...</option>
//             <option value="EDUCATION">Education</option>
//             <option value="MEDICAL">Medical</option>
//             <option value="VENTURE">Venture</option>
//             <option value="PERSONAL">Personal</option>
//             <option value="DEBTCONSOLIDATION">Debt Consolidation</option>
//             <option value="HOMEIMPROVEMENT">Home Improvement</option>
//           </select>
//         </div>

//         <div className="input-group">
//           <label>Loan Grade</label>
//           <select name="loan_grade" required onChange={handleChange}>
//             <option value="">Select...</option>
//             <option value="A">A</option>
//             <option value="B">B</option>
//             <option value="C">C</option>
//             <option value="D">D</option>
//             <option value="E">E</option>
//             <option value="F">F</option>
//             <option value="G">G</option>
//           </select>
//         </div>

//         <div className="input-group">
//           <label>Historical Default?</label>
//           <select name="cb_person_default_on_file" required onChange={handleChange}>
//             <option value="">Select...</option>
//             <option value="Y">Yes</option>
//             <option value="N">No</option>
//           </select>
//         </div>
//         <button type="submit">Run AI Prediction</button>
//       </form>

//       {result && (
//         <div className={`result-box ${result.status.includes('APPROVE') ? 'approve' : 'reject'}`}>
//           {result.status} <br/>
//           <span style={{fontSize: '14px', fontWeight: 'normal'}}>Risk Score: {result.risk_score}</span>
//         </div>
//       )}
//     </div>
//   )
// }

// export default App
// App.jsx
import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('single')

  // --- STATE FOR SINGLE PREDICTION ---
  const [formData, setFormData] = useState({
    person_age: '',
    person_income: '',
    person_home_ownership: '',
    person_emp_length: '',
    loan_intent: '',
    loan_grade: '',
    loan_amnt: '',
    loan_int_rate: '',
    loan_percent_income: '',
    cb_person_default_on_file: '',
    cb_person_cred_hist_length: ''
  })
  const [result, setResult] = useState(null)

  // --- STATE FOR BULK UPLOAD ---
  const [file, setFile] = useState(null)
  const [bulkMessage, setBulkMessage] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [totalExpected, setTotalExpected] = useState(0)
  const [isReady, setIsReady] = useState(false)

  const gradeToInterestRate = {
    A: 6.5, B: 9.5, C: 13.5, D: 16.5, E: 19.5, F: 22.5, G: 25.5
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    let updatedFormData = { ...formData, [name]: value };

    if (name === 'loan_grade' && value !== '') {
      updatedFormData.loan_int_rate = gradeToInterestRate[value];
    }
    setFormData(updatedFormData);
  }

  // --- 1. SINGLE APPLICANT HANDLER ---
  const handleSingleSubmit = async (e) => {
    e.preventDefault()
    
    const payload = {
      person_age: Number(formData.person_age),
      person_income: Number(formData.person_income),
      person_home_ownership: formData.person_home_ownership,
      person_emp_length: Number(formData.person_emp_length),
      loan_intent: formData.loan_intent,
      loan_grade: formData.loan_grade,
      loan_amnt: Number(formData.loan_amnt),
      loan_int_rate: Number(formData.loan_int_rate),
      loan_percent_income: Number(formData.loan_percent_income),
      cb_person_default_on_file: formData.cb_person_default_on_file,
      cb_person_cred_hist_length: Number(formData.cb_person_cred_hist_length)
    }

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/predict/', payload)
      setResult(response.data)
    } catch (error) {
      console.error("API Error:", error)
      alert("Failed to connect to the API. Ensure the server is running.")
    }
  }

  // --- 2. DYNAMIC POLLING LOGIC FOR BULK UPLOAD ---
  const handleBulkSubmit = async (e) => {
    e.preventDefault()
    if (!file) return

    setIsProcessing(true)
    setIsReady(false)
    setProgress(0)
    setTotalExpected(0)
    setBulkMessage("Uploading to Kafka Queue...")

    const uploadData = new FormData()
    uploadData.append('file', file)

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/upload-csv/', uploadData)
      const { batch_id, expected_count, message } = response.data;
      
      setTotalExpected(expected_count)
      setBulkMessage(message)

      // Ping the database every 2 seconds to check worker progress
      const interval = setInterval(async () => {
        try {
          const statusRes = await axios.get(`http://127.0.0.1:8000/api/check-batch/?batch_id=${batch_id}&expected=${expected_count}`)
          
          setProgress(statusRes.data.processed)

          // If PyTorch is finished, stop polling and show the blinking button!
          if (statusRes.data.is_ready) {
            clearInterval(interval)
            setIsProcessing(false)
            setIsReady(true)
            setBulkMessage("Batch Processing Complete!")
          }
        } catch (err) {
          console.error("Polling error", err)
          clearInterval(interval)
          setIsProcessing(false)
          setBulkMessage("Failed to get progress update. Check your Django terminal for backend errors.")
        }
      }, 2000)

    } catch (error) {
      setBulkMessage("Upload failed. Ensure the server and background queues are running.")
      setIsProcessing(false)
    }
  }

  return (
    <div className="form-container">
      <h2>Credit Risk EWS</h2>

      {/* TAB NAVIGATION */}
      <div className="tab-container">
        <button 
          type="button"
          className={`tab-btn ${activeTab === 'single' ? 'active' : ''}`}
          onClick={() => setActiveTab('single')}
        >
          Single Applicant
        </button>
        <button 
          type="button"
          className={`tab-btn ${activeTab === 'bulk' ? 'active' : ''}`}
          onClick={() => setActiveTab('bulk')}
        >
          Bulk Upload
        </button>
      </div>

      {/* TAB 1: SINGLE PREDICTION FORM */}
      {activeTab === 'single' && (
        <form onSubmit={handleSingleSubmit}>
          <div className="input-group">
            <label>Applicant Age</label>
            <input type="number" name="person_age" required onChange={handleChange} placeholder="e.g., 28" />
          </div>
          
          <div className="input-group">
            <label>Annual Income ($)</label>
            <input type="number" name="person_income" required onChange={handleChange} placeholder="e.g., 65000" />
          </div>

          <div className="input-group">
            <label>Requested Loan Amount ($)</label>
            <input type="number" name="loan_amnt" required onChange={handleChange} placeholder="e.g., 15000" />
          </div>
          
          <div className="input-group">
            <label>Employment Length (Years)</label>
            <input type="number" name="person_emp_length" required onChange={handleChange} />
          </div>

          <div className="input-group">
            <label>Interest Rate (%)</label>
            <input type="number" step="0.01" name="loan_int_rate" value={formData.loan_int_rate} required onChange={handleChange} />
          </div>

          <div className="input-group">
            <label>Loan Percent of Income (e.g., 0.20)</label>
            <input type="number" step="0.01" name="loan_percent_income" required onChange={handleChange} />
          </div>

          <div className="input-group">
            <label>Credit History Length (Years)</label>
            <input type="number" name="cb_person_cred_hist_length" required onChange={handleChange} />
          </div>

          <div className="input-group">
            <label>Home Ownership</label>
            <select name="person_home_ownership" required onChange={handleChange}>
              <option value="">Select...</option>
              <option value="RENT">Rent</option>
              <option value="OWN">Own</option>
              <option value="MORTGAGE">Mortgage</option>
              <option value="OTHER">Other</option>
            </select>
          </div>

          <div className="input-group">
            <label>Loan Intent</label>
            <select name="loan_intent" required onChange={handleChange}>
              <option value="">Select...</option>
              <option value="EDUCATION">Education</option>
              <option value="MEDICAL">Medical</option>
              <option value="VENTURE">Venture</option>
              <option value="PERSONAL">Personal</option>
              <option value="DEBTCONSOLIDATION">Debt Consolidation</option>
              <option value="HOMEIMPROVEMENT">Home Improvement</option>
            </select>
          </div>

          <div className="input-group">
            <label>Loan Grade</label>
            <select name="loan_grade" required onChange={handleChange}>
              <option value="">Select...</option>
              <option value="A">A</option>
              <option value="B">B</option>
              <option value="C">C</option>
              <option value="D">D</option>
              <option value="E">E</option>
              <option value="F">F</option>
              <option value="G">G</option>
            </select>
          </div>

          <div className="input-group">
            <label>Historical Default?</label>
            <select name="cb_person_default_on_file" required onChange={handleChange}>
              <option value="">Select...</option>
              <option value="Y">Yes</option>
              <option value="N">No</option>
            </select>
          </div>
          
          <button type="submit">Run Prediction</button>

          {result && (
            <div className={`result-box ${result.status.includes('APPROVE') ? 'approve' : 'reject'}`}>
              {result.status} <br/>
              <span style={{fontSize: '14px', fontWeight: 'normal'}}>Risk Score: {result.risk_score}</span>
            </div>
          )}
        </form>
      )}

      {/* TAB 2: BULK CSV UPLOAD FORM */}
      {activeTab === 'bulk' && (
        <form onSubmit={handleBulkSubmit}>
          <div className="input-group">
            <label>Upload Application Batch (.csv)</label>
            <input 
              type="file" 
              accept=".csv" 
              required
              onChange={(e) => setFile(e.target.files[0])} 
              style={{ padding: '10px' }} 
            />
          </div>
          
          <button type="submit" disabled={isProcessing}>
            {isProcessing ? "Processing..." : "Process Batch Upload"}
          </button>

          {bulkMessage && (
            <div className="result-box approve" style={{ marginTop: '15px' }}>
              {bulkMessage}
              
              {/* LIVE PROGRESS COUNTER */}
              {isProcessing && totalExpected > 0 && (
                <div style={{ marginTop: '10px', fontSize: '14px', color: '#555' }}>
                  Worker Progress: {progress} / {totalExpected} rows processed
                </div>
              )}
            </div>
          )}

          {/* THIS BUTTON ONLY APPEARS AND BLINKS WHEN FINISHED */}
          {isReady && (
            <div style={{ textAlign: 'center', marginTop: '30px' }}>
              <button 
                type="button" 
                className="btn-ready-blink"
                onClick={() => window.open('http://127.0.0.1:8000/api/download-csv/', '_blank')}
              >
                Download AI Predictions (.csv)
              </button>
            </div>
          )}
        </form>
      )}
    </div>
  )
}

export default App