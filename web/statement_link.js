// Builds the "Download statement" link shown in the customer portal.
export function statementLink(accountId, format) {
  const safeFormat = format === "pdf" ? "pdf" : "csv";
  return `/statements/${accountId}/download?format=${safeFormat}`;
}
