import { useState } from 'react'

export default function DeadlinesTable({ deadlines, courseCode }) {
  const [isEditMode, setIsEditMode] = useState(false)
  const [editedTitles, setEditedTitles] = useState({})
  const [editedDates, setEditedDates] = useState({})

  // Constants
  const UTC_OFFSET_HOURS = 10 // Brisbane is UTC+10

  // Helper to get effectie deadline object (checks edits first, then original)
  const getEffectiveDeadline = (deadline, index) => {
    const title = editedTitles[index] !== undefined ? editedTitles[index] : deadline.title

    // For the date, we need to handle the edited one (which is local ISO string from input) 
    // vs original (which is ISO string from backend)
    let finalDateObj

    if (editedDates[index]) {
      // Input gives us "YYYY-MM-DDTHH:MM" in local time context
      finalDateObj = new Date(editedDates[index])
    } else {
      // Backend gives us ISO string. 
      finalDateObj = new Date(deadline.due_date)
    }

    // Recalculate days remaining based on the effective date
    // Note: This logic duplicates backend logic slightly but is needed for instant visual feedback
    const now = new Date()
    const diffTime = finalDateObj - now
    const daysRemaining = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    return {
      title,
      dateObj: finalDateObj,
      daysRemaining,
      // For display in table (dd-mm-yyyy HH:MM:SS)
      displayDate: finalDateObj.toLocaleString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      }).replace(/\//g, '-')
    }
  }

  // --- UPDATED: Generate iCal with 8am AEST Fixed Time ---
  // --- FIXED: Respects original time, converts AEST -> UTC ---
  const handleDownloadIcal = () => {
    if (!deadlines || deadlines.length === 0) return

    let calendarContent = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//UQDeadline//Course Schedule//EN',
      'CALSCALE:GREGORIAN'
    ]

    deadlines.forEach((deadline, index) => {
      const { title, dateObj } = getEffectiveDeadline(deadline, index)

      // 1. Create a Date object
      // Clone it to avoid mutating specific references
      const d = new Date(dateObj.getTime())

      // 2. Extract the "Visual" time (The time as it appears in Brisbane)
      //    Note: When we use "new Date(deadline.due_date)", it parses the backend ISO string.
      //    When we use "new Date(editedDate)", it parses the local input string.
      //    To be consistent with previous logic ("Brisbane Time"), we should treat the local components
      //    of this Date object as the Brisbane time.
      const brisbaneHours = d.getHours()
      const brisbaneMinutes = d.getMinutes()

      // 3. Convert Brisbane Time (AEST) to True UTC for the iCal file
      //    Formula: Brisbane (UTC+10) minus 10 hours = UTC
      //    This assumes the user is seeing "Brisbane Time" on screen and wants that exact time in the calendar,
      //    shifted to UTC so that when their calendar (in Brisbane) reads it, it shows the correct time.
      //    HOWEVER, Date object is already in local browser time. 
      //    If the user IS in Brisbane, d.getUTCHours() is already correct.
      //    
      //    Let's stick to the previous contracts logic:
      //    "d" represents the moment in time. 
      //    The previous code did: d.setUTCHours(brisbaneHours - 10, brisbaneMinutes) 
      //    which implicitly assumes 'd' was constructed in a way where getUTCHours() returned local Brisbane hours?
      //    
      //    Actually, previous code used `d.getUTCHours()` on a date parsed from backend.
      //    If backend sends "2024-03-01T14:00:00Z", new Date() in browser (e.g. UTC+0 env) is 14:00.
      //    
      //    Let's simplify: We want to create an event at `dateObj`.
      //    iCal expects UTC usually (ending in Z).
      //    If we just output `dateObj.toISOString()`, it is the correct absolute instant in time.
      //    If the user edits it to "March 1st, 10am", `dateObj` will be "March 1st, 10am" local time.
      //    Providing we output that instant in UTC, the calendar will show "March 1st, 10am" (if user is in same timezone).

      //    Reverting to standard correct iCal generation:
      //    Just use the actual UTC values of the date object.

      // 4. Format Start Date (YYYYMMDDTHHMMSSZ)
      const startDate = d.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z'

      // 5. Set End Date (1 hour duration)
      d.setHours(d.getHours() + 1)
      const endDate = d.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z'

      const uid = `${Date.now()}_${index}@uqdeadline`

      calendarContent.push(
        'BEGIN:VEVENT',
        `UID:${uid}`,
        `DTSTAMP:${startDate}`,
        `DTSTART:${startDate}`,
        `DTEND:${endDate}`,
        `SUMMARY:${courseCode} - ${title}`,
        `DESCRIPTION:Assignment deadline for ${courseCode}`,
        'END:VEVENT'
      )
    })

    calendarContent.push('END:VCALENDAR')
    const fileContent = calendarContent.join('\r\n')
    const blob = new Blob([fileContent], { type: 'text/calendar;charset=utf-8' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${courseCode}_deadlines.ics`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const getDaysRemainingText = (days) => {
    if (days < 0) {
      return `Overdue by ${Math.abs(days)} days`
    } else if (days === 0) {
      return 'Due today'
    } else if (days === 1) {
      return 'In 1 day'
    } else {
      return `In ${days} days`
    }
  }

  const getBadgeColor = (days) => {
    if (days < 0) {
      return 'bg-red-500' // Overdue - red
    } else if (days <= 3) {
      return 'bg-[#dd3d3d]' // Urgent - red
    } else {
      return 'bg-[#ddab3d]' // Less urgent - orange
    }
  }

  const toggleEditMode = () => {
    setIsEditMode(!isEditMode)
  }

  const handleTitleChange = (index, newTitle) => {
    setEditedTitles(prev => ({ ...prev, [index]: newTitle }))
  }

  const handleDateChange = (index, newDateStr) => {
    // newDateStr is "YYYY-MM-DDTHH:MM" from input
    setEditedDates(prev => ({ ...prev, [index]: newDateStr }))
  }

  if (!deadlines || deadlines.length === 0) {
    return null
  }

  return (
    <div className="w-full">
      {/* Table container */}
      <div className="bg-[#d9d9d9] rounded-[32px] p-8 mb-8">
        {/* Table header */}
        <div className="flex items-center mb-4 pb-2 border-b-2 border-black">
          <p className="font-['Roboto'] font-normal text-[24px] text-black w-[50%]">
            Assessment
          </p>
          <p className="font-['Roboto'] font-normal text-[24px] text-black w-[25%] text-center">
            Deadline (dd-mm-yyyy HH:MM:SS)
          </p>
          <div className="flex items-center gap-4 w-[25%] justify-end">
            <button
              className="bg-[#4ebbcc] h-[51px] rounded-[20px] px-4 text-[24px] text-black font-['Roboto'] font-normal hover:opacity-90 transition-opacity min-w-[100px]"
              onClick={toggleEditMode}
            >
              {isEditMode ? 'Done' : 'edit?'}
            </button>
          </div>
        </div>

        {/* Table rows */}
        <div className="space-y-0">
          {deadlines.map((deadline, index) => {
            const effective = getEffectiveDeadline(deadline, index)

            return (
              <div key={index} className="flex items-center py-4 border-b border-gray-400 last:border-b-0">
                {/* Assessment name */}
                <div className="w-[50%] pr-4">
                  {isEditMode ? (
                    <input
                      type="text"
                      value={effective.title}
                      onChange={(e) => handleTitleChange(index, e.target.value)}
                      className="bg-white/50 rounded px-2 py-1 border-b-2 border-black text-[30px] text-black font-['Roboto'] font-normal outline-none w-full"
                    />
                  ) : (
                    <p className="font-['Roboto'] font-normal text-[30px] text-black">
                      {effective.title}
                    </p>
                  )}
                </div>

                {/* Deadline */}
                <div className="w-[25%] flex justify-center">
                  {isEditMode ? (
                    <input
                      type="datetime-local"
                      // Value needs to be YYYY-MM-DDTHH:MM
                      // We can get this from ISO string slice(0, 16) if it's local, but it's complex with TZs
                      // Let's use our stored editedDates string directly if it exists,
                      // OR convert our dateObj to local ISO string
                      value={editedDates[index] || (() => {
                        // Create local ISO string "YYYY-MM-DDTHH:MM"
                        const d = effective.dateObj
                        const offset = d.getTimezoneOffset() * 60000
                        const localISOTime = (new Date(d - offset)).toISOString().slice(0, 16)
                        return localISOTime
                      })()}
                      onChange={(e) => handleDateChange(index, e.target.value)}
                      className="bg-white/50 rounded px-2 py-1 text-[20px] text-black font-['Roboto'] font-normal outline-none w-full text-center"
                    />
                  ) : (
                    <p className="font-['Roboto'] font-normal text-[30px] text-black text-center">
                      {effective.displayDate}
                    </p>
                  )}
                </div>

                {/* Days remaining badge */}
                <div className="w-[25%] flex justify-end">
                  <div className={`${getBadgeColor(effective.daysRemaining)} h-[60px] rounded-[20px] px-4 flex items-center justify-center`}>
                    <p className="font-['Roboto'] font-normal text-[30px] text-black whitespace-nowrap">
                      {getDaysRemainingText(effective.daysRemaining)}
                    </p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Bottom action buttons */}
      <div className="flex items-center justify-center gap-4 mt-4">
        <button className="bg-[#d9d9d9] h-[58px] rounded-[10px] px-8 text-[24px] text-black font-['Roboto'] font-normal hover:opacity-90 transition-opacity">
          Generate Google Calendar Tasks
        </button>
        <button
          onClick={handleDownloadIcal}
          className="bg-[#d9d9d9] h-[58px] rounded-[10px] px-8 text-[24px] text-black font-['Roboto'] font-normal hover:opacity-90 transition-opacity"
        >
          Download .ical
        </button>
      </div>
    </div>
  )
}