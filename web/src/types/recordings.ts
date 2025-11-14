export interface Recording {
  id: string;
  date: Date;
  startTime: string;
  endTime: string;
  duration: number; // in seconds
  thumbnailUrl?: string;
  videoUrl: string;
}

export interface DayRecordings {
  date: Date;
  recordings: Recording[];
}
