import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface CalendarViewProps {
  datesWithRecordings: Date[];
  selectedDate: Date | null;
  onDateSelect: (date: Date) => void;
}

export const CalendarView = ({
  datesWithRecordings,
  selectedDate,
  onDateSelect,
}: CalendarViewProps) => {
  const [currentMonth, setCurrentMonth] = useState(new Date());

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    return { daysInMonth, startingDayOfWeek };
  };

  const hasRecordings = (date: Date) => {
    return datesWithRecordings.some(
      (d) =>
        d.getDate() === date.getDate() &&
        d.getMonth() === date.getMonth() &&
        d.getFullYear() === date.getFullYear()
    );
  };

  const isSelectedDate = (date: Date) => {
    if (!selectedDate) return false;
    return (
      date.getDate() === selectedDate.getDate() &&
      date.getMonth() === selectedDate.getMonth() &&
      date.getFullYear() === selectedDate.getFullYear()
    );
  };

  const { daysInMonth, startingDayOfWeek } = getDaysInMonth(currentMonth);

  const prevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  const monthName = currentMonth.toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
  });

  const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  return (
    <div className="bg-card rounded-lg p-6 border border-border">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-foreground">{monthName}</h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={prevMonth}
            className="bg-secondary hover:bg-secondary/80"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={nextMonth}
            className="bg-secondary hover:bg-secondary/80"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-2 mb-2">
        {weekDays.map((day) => (
          <div
            key={day}
            className="text-center text-sm font-medium text-muted-foreground py-2"
          >
            {day}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-2">
        {Array.from({ length: startingDayOfWeek }).map((_, i) => (
          <div key={`empty-${i}`} />
        ))}
        {Array.from({ length: daysInMonth }).map((_, i) => {
          const day = i + 1;
          const date = new Date(
            currentMonth.getFullYear(),
            currentMonth.getMonth(),
            day
          );
          const hasRec = hasRecordings(date);
          const isSelected = isSelectedDate(date);

          return (
            <button
              key={day}
              onClick={() => hasRec && onDateSelect(date)}
              disabled={!hasRec}
              className={cn(
                "relative aspect-square rounded-lg flex flex-col items-center justify-center text-sm transition-all gap-1",
                "hover:bg-nvr-surface-hover",
                hasRec
                  ? "bg-nvr-clip-bg cursor-pointer text-foreground font-semibold border border-primary/20 shadow-[0_0_12px_rgba(14,165,233,0.15)] hover:shadow-[0_0_20px_rgba(14,165,233,0.25)] hover:border-primary/40"
                  : "bg-muted/50 text-muted-foreground cursor-not-allowed font-medium",
                isSelected && "ring-2 ring-primary bg-primary/10 shadow-[0_0_24px_rgba(14,165,233,0.35)]"
              )}
            >
              <span>{day}</span>
              {hasRec && (
                <div className="w-1.5 h-1.5 rounded-full bg-nvr-recording-indicator shadow-[0_0_8px_rgba(14,165,233,0.6)] animate-pulse" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};
