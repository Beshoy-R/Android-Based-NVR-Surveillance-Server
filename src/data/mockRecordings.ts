import { Recording, DayRecordings } from "@/types/recordings";

// Generate mock recordings for the past 30 days
const generateMockRecordings = (): DayRecordings[] => {
  const recordings: DayRecordings[] = [];
  const today = new Date();
  
  // Generate recordings for random days in the past 30 days
  const daysWithRecordings = [1, 2, 5, 7, 10, 12, 15, 18, 20, 23, 25, 28];
  
  daysWithRecordings.forEach((daysAgo) => {
    const date = new Date(today);
    date.setDate(date.getDate() - daysAgo);
    date.setHours(0, 0, 0, 0);
    
    const dayRecordings: Recording[] = [];
    
    // Generate 3-7 random clips for each day
    const clipCount = Math.floor(Math.random() * 5) + 3;
    
    for (let i = 0; i < clipCount; i++) {
      const hour = Math.floor(Math.random() * 24);
      const minute = Math.floor(Math.random() * 60);
      const duration = Math.floor(Math.random() * 120) + 30; // 30-150 seconds
      
      const startTime = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
      const endMinute = minute + Math.floor(duration / 60);
      const endHour = hour + Math.floor(endMinute / 60);
      const endTime = `${(endHour % 24).toString().padStart(2, '0')}:${(endMinute % 60).toString().padStart(2, '0')}`;
      
      dayRecordings.push({
        id: `rec-${date.getTime()}-${i}`,
        date,
        startTime,
        endTime,
        duration,
        videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
      });
    }
    
    // Sort recordings by start time
    dayRecordings.sort((a, b) => a.startTime.localeCompare(b.startTime));
    
    recordings.push({
      date,
      recordings: dayRecordings,
    });
  });
  
  return recordings.sort((a, b) => b.date.getTime() - a.date.getTime());
};

export const mockRecordings = generateMockRecordings();

export const getRecordingsForDate = (date: Date): Recording[] => {
  const targetDate = new Date(date);
  targetDate.setHours(0, 0, 0, 0);
  
  const dayRecordings = mockRecordings.find(
    (dr) => dr.date.getTime() === targetDate.getTime()
  );
  
  return dayRecordings?.recordings || [];
};

export const getDatesWithRecordings = (): Date[] => {
  return mockRecordings.map((dr) => dr.date);
};
