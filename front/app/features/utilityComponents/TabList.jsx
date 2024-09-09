import React, { useState } from 'react';

/**
 * Navigation tab component. Accepts a list of TabItems, displaying them one at
 * a time when clicking on the button that has the same index.
 * @param {array} tabs List of TabItems
 * @returns
 */
export const TabList = ({ tabs, activeTabIndex = 0 }) => {
  const [activeTab, setActiveTab] = useState(activeTabIndex);

  const handleTabClick = (index) => {
    setActiveTab(index);
  };

  return (
    <div className="tabs">
      <nav className="tab-list-wrapper">
        <ul className="tab-list" role="tablist" aria-orientation="horizontal">
          {tabs.map((tab, index) => {
            const labelWithoutSpaces = tab.props.label.split(' ').join('');
            return (
              <li key={`tab-${index}`}>
                <button
                  key={`tab-btn-${index}`}
                  role="tab"
                  id={`tab-${labelWithoutSpaces}`}
                  aria-controls={`panel-${labelWithoutSpaces}`}
                  aria-selected={activeTab === index}
                  onClick={() => handleTabClick(index)}
                  className={`tab-btn ${
                    activeTab === index && 'tab-btn--active'
                  }`}
                >
                  {tab.props.label}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>
      {tabs[activeTab]}
    </div>
  );
};
