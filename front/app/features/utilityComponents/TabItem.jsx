/**
 * TabItem component
 * @param {string} label TabItem's name in the UI
 * @param {string} id TabItem's id
 * @returns
 */
export const TabItem = ({ label, id, children }) => {
  const labelWithoutSpaces = label.split(' ').join('');

  return (
    <div
      className="tab-panel"
      role="tabpanel"
      aria-labelledby={`tab-${labelWithoutSpaces}`}
      id={id}
    >
      {children}
    </div>
  );
};
