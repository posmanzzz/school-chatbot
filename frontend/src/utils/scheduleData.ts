import { ScheduleData, ScheduleAlert } from '../types';

export const SCHEDULE_DATA: ScheduleData = {
  exams: [
    { start: '2025-05-19', end: '2025-05-23', name: '前期中間試験' },
    { start: '2025-07-14', end: '2025-07-18', name: '前期期末試験' },
    { start: '2025-10-20', end: '2025-10-24', name: '後期中間試験' },
    { start: '2025-12-15', end: '2025-12-19', name: '後期期末試験' },
    { start: '2026-02-17', end: '2026-02-21', name: '学年末試験' },
  ],
  holidays: [
    { start: '2025-03-21', end: '2025-04-06', name: '春休み' },
    { start: '2025-07-26', end: '2025-08-31', name: '夏休み' },
    { start: '2025-12-25', end: '2026-01-07', name: '冬休み' },
    { start: '2026-03-21', end: '2026-04-06', name: '春休み' },
  ],
  closedDays: [
    { date: '2025-04-29', name: '昭和の日' },
    { date: '2025-05-03', name: '憲法記念日' },
    { date: '2025-05-04', name: 'みどりの日' },
    { date: '2025-05-05', name: 'こどもの日' },
    { date: '2025-05-06', name: '振替休日' },
    { date: '2025-07-21', name: '海の日' },
    { date: '2025-08-11', name: '山の日' },
    { date: '2025-09-15', name: '敬老の日' },
    { date: '2025-09-23', name: '秋分の日' },
    { date: '2025-10-13', name: 'スポーツの日' },
    { date: '2025-11-03', name: '文化の日' },
    { date: '2025-11-23', name: '勤労感謝の日' },
    { date: '2025-11-24', name: '振替休日' },
    { date: '2026-01-01', name: '元日' },
    { date: '2026-01-13', name: '成人の日' },
    { date: '2026-02-11', name: '建国記念の日' },
    { date: '2026-02-23', name: '天皇誕生日' },
    { date: '2026-03-20', name: '春分の日' },
  ],
  events: [
    { date: '2025-04-07', name: '入学式' },
    { date: '2025-04-08', name: '始業式' },
    { date: '2025-06-14', name: '体育祭' },
    { date: '2025-10-25', name: '高専祭' },
    { date: '2025-10-26', name: '高専祭' },
    { date: '2025-03-19', name: '卒業式' },
  ],
};

export function checkScheduleAlerts(): ScheduleAlert[] {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const alerts: ScheduleAlert[] = [];

  // テスト前チェック（7日前から警告）
  SCHEDULE_DATA.exams.forEach((exam) => {
    const startDate = new Date(exam.start);
    const endDate = new Date(exam.end);
    const daysUntil = Math.ceil(
      (startDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (daysUntil > 0 && daysUntil <= 7) {
      alerts.push({
        type: 'exam',
        icon: 'warning',
        color: '#ef4444',
        title: `${exam.name}まであと${daysUntil}日`,
        message: `${exam.start.slice(5).replace('-', '/')}〜${exam.end.slice(5).replace('-', '/')} は${exam.name}です。勉強頑張りましょう！`,
      });
    } else if (daysUntil <= 0 && today <= endDate) {
      alerts.push({
        type: 'exam',
        icon: 'edit',
        color: '#ef4444',
        title: `${exam.name}期間中`,
        message: '試験期間中です。最後まで頑張りましょう！',
      });
    }
  });

  // 長期休暇チェック（7日前から通知）
  SCHEDULE_DATA.holidays.forEach((holiday) => {
    const startDate = new Date(holiday.start);
    const endDate = new Date(holiday.end);
    const daysUntil = Math.ceil(
      (startDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (daysUntil > 0 && daysUntil <= 7) {
      alerts.push({
        type: 'holiday',
        icon: 'sun',
        color: '#22c55e',
        title: `${holiday.name}まであと${daysUntil}日`,
        message: `${holiday.start.slice(5).replace('-', '/')}から${holiday.name}が始まります！`,
      });
    } else if (daysUntil <= 0 && today <= endDate) {
      const daysLeft = Math.ceil(
        (endDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
      );
      alerts.push({
        type: 'holiday',
        icon: 'sun',
        color: '#22c55e',
        title: `${holiday.name}中`,
        message: `${holiday.name}です。残り${daysLeft}日、楽しんでください！`,
      });
    }
  });

  // 祝日チェック（3日前から通知）
  SCHEDULE_DATA.closedDays.forEach((day) => {
    const date = new Date(day.date);
    const daysUntil = Math.ceil(
      (date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (daysUntil > 0 && daysUntil <= 3) {
      alerts.push({
        type: 'closed',
        icon: 'calendar',
        color: '#3b82f6',
        title: `${daysUntil}日後は${day.name}`,
        message: `${day.date.slice(5).replace('-', '/')}（${day.name}）は休みです。`,
      });
    }
  });

  // 学校行事チェック（7日前から通知）
  SCHEDULE_DATA.events.forEach((event) => {
    const date = new Date(event.date);
    const daysUntil = Math.ceil(
      (date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (daysUntil > 0 && daysUntil <= 7) {
      alerts.push({
        type: 'event',
        icon: 'star',
        color: '#f59e0b',
        title: `${event.name}まであと${daysUntil}日`,
        message: `${event.date.slice(5).replace('-', '/')}は${event.name}です！`,
      });
    } else if (daysUntil === 0) {
      alerts.push({
        type: 'event',
        icon: 'star',
        color: '#f59e0b',
        title: `今日は${event.name}`,
        message: `${event.name}の日です！`,
      });
    }
  });

  return alerts;
}
