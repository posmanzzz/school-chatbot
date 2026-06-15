import { useState, useEffect } from 'react';
import { ScheduleAlert } from '../types';
import { checkScheduleAlerts } from '../utils/scheduleData';

export function useScheduleAlerts() {
  const [alerts, setAlerts] = useState<ScheduleAlert[]>([]);
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set());

  useEffect(() => {
    const scheduleAlerts = checkScheduleAlerts();
    setAlerts(scheduleAlerts);
  }, []);

  const dismissAlert = (index: number) => {
    const alert = alerts[index];
    if (alert) {
      setDismissedAlerts((prev) => new Set([...prev, `${alert.type}-${alert.title}`]));
    }
  };

  const visibleAlerts = alerts.filter(
    (alert) => !dismissedAlerts.has(`${alert.type}-${alert.title}`)
  );

  return {
    alerts: visibleAlerts,
    dismissAlert,
  };
}
