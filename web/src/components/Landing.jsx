import { useState } from 'react'
import DeadlinesTable from './DeadlinesTable'

export default function Landing() {
  const [courseCode, setCourseCode] = useState('')
  const [showDisclaimer, setShowDisclaimer] = useState(true)
  const [deadlines, setDeadlines] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleReset = () => {
    setCourseCode('')
    setDeadlines([])
    setError(null)
    setShowDisclaimer(true)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleFetchDeadlines = async () => {
    if (!courseCode.trim()) {
      setError('Please enter a course code')
      return
    }

    setLoading(true)
    setError(null)
    setDeadlines([])

    try {
      const response = await fetch(`http://localhost:5000/api/course/${courseCode.trim().toUpperCase()}`)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch deadlines')
      }

      // Sort deadlines chronologically (earliest first)
      const sortedDeadlines = (data.deadlines || []).sort((a, b) => {
        const dateA = new Date(a.due_date)
        const dateB = new Date(b.due_date)
        return dateA - dateB
      })
      setDeadlines(sortedDeadlines)
      if (sortedDeadlines.length === 0) {
        setError('No deadlines found for this course')
      }
    } catch (err) {
      setError(err.message || 'An error occurred while fetching deadlines')
      console.error('Error fetching deadlines:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading) {
      handleFetchDeadlines()
    }
  }

  return (
    <div className="bg-[#48206c] relative w-full min-h-screen" data-name="Landing" data-node-id="1:6">
      {/* Top gradient header */}
      <div 
        className="absolute h-[276px] left-0 top-0 w-full z-0" 
        data-node-id="8:2" 
        style={{ 
          backgroundImage: "linear-gradient(180.477deg, rgb(102, 66, 135) 1.9094%, rgb(72, 32, 108) 97.751%)" 
        }} 
      />

      {/* Main content container */}
      <div className="relative z-10 flex flex-col items-center px-5 pb-16 w-full">
        {/* UQDeadline title - clickable to reset page/table */}
        <div className="w-full max-w-[1200px] flex items-center justify-between pt-8">
          <button
            type="button"
            onClick={handleReset}
            className="font-['Roboto'] font-normal leading-normal text-[40px] whitespace-nowrap text-white hover:opacity-80 transition-opacity"
            data-node-id="8:6"
          >
            UQDeadline
          </button>
        </div>

        {/* Subtitle */}
        <p 
          className="font-['Roboto'] font-normal leading-normal text-[40px] whitespace-nowrap text-white mt-[40px] mb-[23px] text-center"
          data-node-id="8:12"
        >
          Get all Deadlines of your courses.
        </p>

        {/* Input and button container (relative, not absolute) */}
        <div className="flex items-center gap-6 w-full max-w-[800px] justify-center">
          {/* Course Code input */}
          <div className="bg-[#d9d9d9] h-[60px] rounded-[10px] flex-1 min-w-[0]" data-node-id="8:7">
            <input
              type="text"
              value={courseCode}
              onChange={(e) => setCourseCode(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Course Code"
              className="bg-transparent h-full w-full px-4 text-[32px] md:text-[40px] text-black font-['Roboto'] font-normal outline-none placeholder:text-black"
            />
          </div>

          {/* Go button */}
          <button
            onClick={handleFetchDeadlines}
            disabled={loading || !courseCode.trim()}
            className="bg-[#88bc40] h-[60px] rounded-[10px] px-8 text-[32px] md:text-[40px] text-black font-['Roboto'] font-normal hover:opacity-90 active:opacity-80 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            data-node-id="8:9"
          >
            {loading ? 'Loading...' : 'Go'}
          </button>
        </div>

        {/* Error message */}
        {error && (
          <p className="mt-4 text-red-500 text-[20px] md:text-[24px] font-['Roboto'] font-normal bg-white/90 px-4 py-2 rounded">
            {error}
          </p>
        )}

        {/* Deadlines table container */}
        {deadlines.length > 0 && (
          // CHANGED: Removed "max-w-[1200px]" and replaced with "w-full"
          // This allows the table to stretch to the edges of the screen (minus the px-5 padding)
          <div className="w-full mt-8">
            <DeadlinesTable deadlines={deadlines} courseCode={courseCode} />
          </div>
        )}
      </div>

      {/* Disclaimer box (only when no deadlines and no course code entered) */}
      {showDisclaimer && deadlines.length === 0 && !courseCode.trim() && (
        <div className="absolute right-[47px] bottom-[88px]">
          <div className="bg-[#d9d9d9] h-[256px] rounded-[49px] w-[488px] p-8 flex flex-col justify-between" data-node-id="15:4">
            <p 
              className="font-['Roboto'] font-normal leading-normal text-[24px] text-black whitespace-pre-line not-italic" 
              data-node-id="15:5"
            >
              Disclaimer:
              {'\n'}This site is not affiliated with UQ.
              {'\n'}Mistakes can occur.
              {'\n'}Please always double check with ECP.
            </p>
            
            <button
              onClick={() => setShowDisclaimer(false)}
              className="bg-[#4798ca] h-[56px] rounded-[20px] w-[280px] text-[40px] text-black font-['Roboto'] font-normal hover:opacity-90 active:opacity-80 transition-opacity self-end flex items-center justify-center"
              data-node-id="25:2"
            >
              Okay!
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

