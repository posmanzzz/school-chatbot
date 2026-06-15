export function getTimeAgo(timestamp: Date | { toDate: () => Date } | null): string {
  if (!timestamp) return '';

  const date = 'toDate' in timestamp ? timestamp.toDate() : new Date(timestamp);
  const now = new Date();
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diff < 60) return 'たった今';
  if (diff < 3600) return `${Math.floor(diff / 60)}分前`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}時間前`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}日前`;

  return date.toLocaleDateString('ja-JP');
}
