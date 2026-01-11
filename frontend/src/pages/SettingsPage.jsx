import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../contexts/AppContext';
import { 
  ChevronLeft, 
  ChevronRight, 
  Check
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import ModeInfoDialog from '../components/profile/ModeInfoDialog';
import { useTranslation } from 'react-i18next';

import UserAvatar from '../components/common/UserAvatar';

export default function SettingsPage() {
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const { 
    currentUser, 
    logout, 
    theme, 
    setTheme 
  } = useAppContext();
  const { toast } = useToast();
  
  // Always return to /chat as per request
  const returnTo = '/chat';
  
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [showThemeModal, setShowThemeModal] = useState(false);
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  const [showModeInfo, setShowModeInfo] = useState(false);
  const [showContactModal, setShowContactModal] = useState(false);
  const [showAboutModal, setShowAboutModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [showModelModal, setShowModelModal] = useState(false);
  const [showPersonalizationModal, setShowPersonalizationModal] = useState(false);

  const handleLogout = () => {
    logout();
    setShowLogoutModal(false);
    navigate('/signin');
    toast({ title: t('settings.logged_out') });
  };

  const showComingSoon = () => {
    toast({ title: t('settings.coming_soon') });
  };

  const getModeDisplay = (mode) => {
    // Check if mode is 'brown' (Deprecated/Removed) and show Gray/Invisible instead or empty?
    // User requested "remove the brown feature writing".
    if (mode === 'brown') {
        // Fallback to Green or Gray display if backend still sends brown
        return `⚪ ${t('mode.gray.name')}`;
    }

    const emojiMap = {
      green: '🟢',
      red: '🔴',
      yellow: '🟡',
      blue: '🔵',
      orange: '🟠',
      gray: '⚪'
    };
    
    if (!mode) return `🟢 ${t('mode.green.name')}`;
    
    return `${emojiMap[mode] || '🟢'} ${t(`mode.${mode}.name`)}`;
  };

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'ja', name: '日本語' },
    { code: 'fr', name: 'Français' },
    { code: 'hi', name: 'हिन्दी' },
    { code: 'zh', name: '中文 (简体)' },
  ];

  const currentLanguageName = languages.find(l => l.code === i18n.language)?.name || 'English';

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-card border-b border-border">
        <div className="px-4 py-3 flex items-center gap-3">
          <button 
            onClick={() => navigate(returnTo)}
            className="p-2 hover:bg-accent rounded-full transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-foreground" />
          </button>
          <h1 className="text-xl font-semibold text-foreground">{t('settings.title')}</h1>
        </div>
      </div>

      {/* Profile Card */}
      <div 
        onClick={() => navigate('/profile')}
        className="bg-card mx-4 mt-4 rounded-xl shadow-sm border border-border p-4 flex items-center gap-3 cursor-pointer hover:shadow-md transition-shadow"
      >
        <UserAvatar 
          src={currentUser?.profilePic} 
          alt={currentUser?.name}
          className="w-14 h-14 rounded-full border-2 border-muted"
          size={28}
        />
        <div className="flex-1">
          <div className="text-base font-semibold text-foreground">
            {currentUser?.name || 'User'}
          </div>
          <div className="text-sm text-muted-foreground">{t('settings.view_profile')}</div>
        </div>
        <ChevronRight className="w-5 h-5 text-muted-foreground" />
      </div>

      {/* Availability Section */}
      <div className="px-4 py-3 mt-6">
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          {t('settings.availability')}
        </h2>
      </div>
      <div className="bg-card mx-4 mt-2 rounded-xl shadow-sm border border-border overflow-hidden">
        <button
          onClick={() => setShowModeInfo(true)}
          className="w-full px-4 py-4 flex items-center justify-between hover:bg-accent transition-colors"
        >
          <div className="flex items-center gap-3">
            <span className="text-xl">🎨</span>
            <div className="text-left">
              <div className="font-medium text-base text-foreground">{t('profile.regulation')}</div>
              <div className="text-sm text-muted-foreground">
                Current: {getModeDisplay(currentUser?.availabilityMode)}
              </div>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-muted-foreground" />
        </button>
      </div>

      {/* App Section */}
      <div className="px-4 py-3 mt-6">
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          {t('settings.app')}
        </h2>
      </div>
      <div className="bg-card mx-4 mt-2 rounded-xl shadow-sm border border-border overflow-hidden">
        <SettingRow 
            icon="🌐" 
            label={t('settings.language')} 
            value={currentLanguageName} 
            onClick={() => setShowLanguageModal(true)} 
        />
        <SettingRow 
            icon="☀️" 
            label={t('settings.theme')} 
            value={theme ? (theme.charAt(0).toUpperCase() + theme.slice(1)) : 'System'} 
            onClick={() => setShowThemeModal(true)} 
        />
        <SettingRow icon="🎨" label={t('settings.personalization')} onClick={() => setShowPersonalizationModal(true)} />
      </div>

      {/* About Section */}
      <div className="px-4 py-3 mt-6">
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          {t('settings.about')}
        </h2>
      </div>
      <div className="bg-card mx-4 mt-2 rounded-xl shadow-sm border border-border overflow-hidden">
        <SettingRow icon="📚" label={t('settings.model')} onClick={() => setShowModelModal(true)} />
        <SettingRow icon="📄" label={t('settings.terms')} onClick={() => setShowTermsModal(true)} />
        <SettingRow icon="🔒" label={t('settings.privacy')} onClick={() => setShowPrivacyModal(true)} />
        <SettingRow icon="ℹ️" label={t('settings.about')} onClick={() => setShowAboutModal(true)} />
      </div>

      {/* Contact Section */}
      <div className="bg-card mx-4 mt-6 rounded-xl shadow-sm border border-border overflow-hidden">
        <SettingRow icon="💬" label={t('settings.contact')} onClick={() => setShowContactModal(true)} />
      </div>

      {/* Danger Zone */}
      <div className="bg-card mx-4 mt-6 rounded-xl shadow-sm border border-border overflow-hidden">
        <SettingRow 
          icon="🚪" 
          label={t('settings.logout')} 
          onClick={() => setShowLogoutModal(true)} 
          showArrow={false}
          isDanger={true}
        />
      </div>

      {/* Theme Modal */}
      {showThemeModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-2xl max-w-sm w-full p-6 shadow-xl border border-border">
            <h3 className="text-lg font-semibold mb-4 text-foreground">{t('settings.theme')}</h3>
            
            <div className="space-y-2">
              {['light', 'dark', 'system'].map((themeOption) => (
                <button
                  key={themeOption}
                  onClick={() => {
                    setTheme(themeOption);
                    setShowThemeModal(false);
                    toast({ title: `Theme updated to ${themeOption}` });
                  }}
                  className={`
                    w-full px-4 py-3 rounded-lg text-left flex items-center justify-between
                    transition-colors border-2
                    ${theme === themeOption 
                      ? 'bg-primary/10 text-primary border-primary' 
                      : 'bg-muted text-foreground border-transparent hover:bg-accent'
                    }
                  `}
                >
                  <span className="capitalize font-medium">{themeOption}</span>
                  {theme === themeOption && (
                    <Check className="w-5 h-5 text-primary" />
                  )}
                </button>
              ))}
            </div>
            
            <button
              onClick={() => setShowThemeModal(false)}
              className="mt-4 w-full py-3 bg-muted text-muted-foreground rounded-lg font-medium hover:bg-accent transition-colors"
            >
              {t('common.cancel')}
            </button>
          </div>
        </div>
      )}

      {/* Language Modal */}
      {showLanguageModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100] p-4">
          <div className="bg-card rounded-2xl max-w-sm w-full p-6 shadow-xl border border-border max-h-[80vh] flex flex-col">
            <h3 className="text-lg font-semibold mb-4 text-foreground flex-shrink-0">{t('settings.language')}</h3>
            
            <div className="space-y-2 overflow-y-auto flex-1 min-h-0">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => {
                    i18n.changeLanguage(lang.code);
                    setShowLanguageModal(false);
                    toast({ title: `Language changed to ${lang.name}` });
                  }}
                  className={`
                    w-full px-4 py-3 rounded-lg text-left flex items-center justify-between
                    transition-colors border-2 shrink-0
                    ${i18n.language === lang.code 
                      ? 'bg-primary/10 text-primary border-primary' 
                      : 'bg-card text-foreground border-muted hover:bg-accent'
                    }
                  `}
                >
                  <span className="font-medium">{lang.name}</span>
                  {i18n.language === lang.code && (
                    <Check className="w-5 h-5 text-primary" />
                  )}
                </button>
              ))}
            </div>
            
            <button
              onClick={() => setShowLanguageModal(false)}
              className="mt-4 w-full py-3 bg-secondary text-secondary-foreground border-2 border-transparent rounded-lg font-medium hover:bg-secondary/80 transition-colors flex-shrink-0 shadow-sm"
            >
              {t('common.cancel')}
            </button>
          </div>
        </div>
      )}

      {/* Logout Modal */}
      {showLogoutModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-2xl max-w-sm w-full p-6 shadow-xl border border-border">
            <h3 className="text-xl font-semibold mb-2 text-foreground">{t('settings.logout')}?</h3>
            <p className="text-muted-foreground mb-6">
              {t('settings.confirm_logout')}
            </p>
            
            <div className="flex gap-3">
              <button
                onClick={() => setShowLogoutModal(false)}
                className="flex-1 py-3 bg-muted text-muted-foreground rounded-lg font-medium hover:bg-accent transition-colors"
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={handleLogout}
                className="flex-1 py-3 bg-destructive text-destructive-foreground rounded-lg font-medium hover:bg-destructive/90 transition-colors"
              >
                {t('settings.logout')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Contact Modal */}
      {showContactModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-2xl max-w-sm w-full p-6 shadow-xl border border-border">
            <h3 className="text-xl font-semibold mb-4 text-foreground">{t('settings.contact')}</h3>
            
            <div className="space-y-4 mb-6">
              <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                <span className="text-xl">📧</span>
                <div className="overflow-hidden">
                  <div className="text-sm text-muted-foreground">Gmail</div>
                  <div className="font-medium text-foreground truncate" title="allenbrowndharak@gmail.com">allenbrowndharak@gmail.com</div>
                </div>
              </div>
              
              <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                <span className="text-xl">📱</span>
                <div>
                  <div className="text-sm text-muted-foreground">Phone No</div>
                  <div className="font-medium text-foreground">+2349168839812</div>
                </div>
              </div>
            </div>
            
            <button
              onClick={() => setShowContactModal(false)}
              className="w-full py-3 bg-muted text-muted-foreground rounded-lg font-medium hover:bg-accent transition-colors"
            >
              {t('common.close')}
            </button>
          </div>
        </div>
      )}

      {/* Personalization Modal */}
      {showPersonalizationModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-2xl max-w-sm w-full p-6 shadow-xl max-h-[80vh] flex flex-col border border-border">
            <h3 className="text-xl font-semibold mb-4 text-foreground flex-shrink-0">Aviato App Personalization</h3>
            
            <div className="overflow-y-auto space-y-4 mb-6 text-sm text-muted-foreground leading-relaxed pr-2">
              <p>Control how people reach you — and how the app treats you.</p>
              
              <h4 className="font-bold text-foreground mt-4">1. Availability Preferences (Core Personalization)</h4>
              <p>Users personalize how reachable they are, not just if.</p>
              <p className="font-medium">Options</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Default availability status</li>
                <li>Auto-switch status by time/day</li>
                <li>Daily message limit</li>
                <li>Priority hours (when reputation effects apply)</li>
                <li>Cooldown mode after X messages</li>
              </ul>
              <p className="font-medium mt-2">Example</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>“Auto-set Red on weekends”</li>
                <li>“Only allow 3 messages per day”</li>
                <li>“Brown mode every weekday 6–8 PM”</li>
              </ul>

              <h4 className="font-bold text-foreground mt-4">2. Messaging Preferences</h4>
              <p>Control what lands in your inbox.</p>
              <p className="font-medium">Settings</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Who can message you (everyone / matches only / verified only)</li>
                <li>Minimum match score required</li>
                <li>First-message length limit</li>
                <li>One-message-per-user rule (until reply)</li>
              </ul>
              <p className="font-medium mt-2">Effect</p>
              <p>Less spam, higher-quality outreach.</p>

              <h4 className="font-bold text-foreground mt-4">3. Reputation Preferences</h4>
              <p>Let users decide how reputation affects them.</p>
              <p className="font-medium">Options</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Show/hide star rating publicly</li>
                <li>Show approval % only when available</li>
                <li>Reputation impact preview before enabling availability</li>
                <li>Ghosting grace window (once per week)</li>
              </ul>
              <p className="font-medium mt-2">Key Rule</p>
              <p>Reputation penalties never apply when unavailable.</p>

              <h4 className="font-bold text-foreground mt-4">4. Match Personalization</h4>
              <p>Users define what matters to them.</p>
              <p className="font-medium">Controls</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Select top 5 interests (weighted)</li>
                <li>Industry focus</li>
                <li>Intent mode (business / hiring / collabs / casual)</li>
                <li>Match strictness slider (Loose → Strict)</li>
              </ul>
              <p className="font-medium mt-2">Result</p>
              <p>Messages come from people who actually align.</p>

              <h4 className="font-bold text-foreground mt-4">5. Notification Control</h4>
              <p>Respect attention, not addiction.</p>
              <p className="font-medium">Options</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Silent mode when Red or Gray</li>
                <li>Digest-only notifications</li>
                <li>Priority alerts for high-match messages</li>
                <li>Timer alerts on/off</li>
              </ul>
              <p>No dark patterns. No pressure.</p>

              <h4 className="font-bold text-foreground mt-4">6. Profile Visibility</h4>
              <p>Personalize how visible you are.</p>
              <p className="font-medium">Modes</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Public profile</li>
                <li>Limited profile (stats only)</li>
                <li>Invisible mode (still searchable by direct link)</li>
              </ul>

              <h4 className="font-bold text-foreground mt-4">7. UI & Tone Personalization</h4>
              <p>Make Aviato feel human.</p>
              <p className="font-medium">Options</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Minimal vs expressive UI</li>
                <li>Humor level in copy (Dry → Playful)</li>
                <li>Color emphasis (neutral vs bold availability colors)</li>
              </ul>

              <h4 className="font-bold text-foreground mt-4">8. Safety Personalization</h4>
              <p>Users choose their boundaries.</p>
              <p className="font-medium">Controls</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Blocked keywords</li>
                <li>Auto-filter low-match messages</li>
                <li>Report thresholds</li>
                <li>One-click block & mute</li>
              </ul>

              <h4 className="font-bold text-foreground mt-4">9. Smart Defaults (Important)</h4>
              <p>For new users:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Start in Gray (Paused)</li>
                <li>Reputation hidden by default</li>
                <li>Matches-only messaging enabled</li>
              </ul>
              <p>This reduces anxiety and builds trust.</p>

              <h4 className="font-bold text-foreground mt-4">Personalization Philosophy (Judges Love This)</h4>
              <p>“Aviato personalizes boundaries, not behavior. We optimize for consent, clarity, and control — not engagement.”</p>

              <h4 className="font-bold text-foreground mt-4">One-Line Summary</h4>
              <p>Aviato adapts to how you want to be contacted, not how often you’re online.</p>
            </div>
            
            <button
              onClick={() => setShowPersonalizationModal(false)}
              className="w-full py-3 bg-muted text-muted-foreground rounded-lg font-medium hover:bg-accent transition-colors flex-shrink-0"
            >
              {t('common.close')}
            </button>
          </div>
        </div>
      )}

      {/* Model Modal */}
      {showModelModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-2xl max-w-sm w-full p-6 shadow-xl max-h-[80vh] flex flex-col border border-border">
            <h3 className="text-xl font-semibold mb-4 text-foreground flex-shrink-0">Aviato App Model</h3>
            
            <div className="overflow-y-auto space-y-4 mb-6 text-sm text-muted-foreground leading-relaxed pr-2">
              <p>A messaging system built on availability, reputation, and accountability.</p>
              
              <h4 className="font-bold text-foreground mt-4">1. User Model</h4>
              <p>Defines who the user is.</p>
              <p className="font-medium">Core fields</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>user_id</li>
                <li>username / display_name</li>
                <li>email</li>
                <li>profile_type (creator, professional, founder, etc.)</li>
                <li>interests (max 5)</li>
                <li>created_at</li>
              </ul>

              <h4 className="font-bold text-foreground mt-4">2. Availability Model</h4>
              <p>(The “Leave me alone” core)</p>
              <p>Controls when and how users can be contacted.</p>
              <p className="font-medium">Fields</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>availability_status (green, yellow, orange, blue, brown, red, gray)</li>
                <li>availability_rules</li>
                <li>time windows</li>
                <li>daily DM limits</li>
                <li>future availability dates</li>
                <li>status_updated_at</li>
              </ul>
              <p className="font-medium mt-2">Rule</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Only one active status at a time</li>
                <li>No penalties when status is unavailable</li>
              </ul>

              <h4 className="font-bold text-foreground mt-4">3. Messaging Model</h4>
              <p>Lightweight, intentional messaging (not full chat).</p>
              <p className="font-medium">Fields</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>message_id</li>
                <li>sender_id</li>
                <li>receiver_id</li>
                <li>message_body</li>
                <li>sent_at</li>
                <li>seen_at</li>
                <li>replied_at</li>
                <li>conversation_id</li>
              </ul>

              <h4 className="font-bold text-foreground mt-4">4. Anti-Ghosting Timer Model</h4>
              <p>Adds accountability without forcing replies.</p>
              <p className="font-medium">Fields</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>timer_started_at</li>
                <li>timer_expires_at (5 hours)</li>
                <li>timer_status (active / completed / expired)</li>
                <li>ghosting_penalty_applied (true / false)</li>
              </ul>
              <p className="font-medium mt-2">Rules</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Timer starts only after a reply</li>
                <li>Applies only when the user is marked available</li>
              </ul>

              <h4 className="font-bold text-foreground mt-4">5. Reputation Model</h4>
              <p>Shows who actually replies.</p>
              <p className="font-medium">Fields</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>star_rating (1–5)</li>
                <li>approval_percentage</li>
                <li>total_interactions</li>
                <li>positive_responses</li>
                <li>negative_responses</li>
                <li>ghosted_count</li>
              </ul>
              <p className="font-medium mt-2">Logic</p>
              <p>Approval % = positive responses ÷ total interactions</p>

              <h4 className="font-bold text-foreground mt-4">6. Match Model</h4>
              <p>Prevents irrelevant outreach.</p>
              <p className="font-medium">Fields</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>interest_overlap_score (0–100%)</li>
                <li>industry_match (true / false)</li>
                <li>match_score (weighted result)</li>
              </ul>
              <p className="font-medium mt-2">Simple logic for MVP:</p>
              <p>shared interests × 20 = match %</p>

              <h4 className="font-bold text-foreground mt-4">7. Review Model</h4>
              <p>Prevents abuse and builds trust.</p>
              <p className="font-medium">Fields</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>review_id</li>
                <li>reviewer_id</li>
                <li>reviewed_user_id</li>
                <li>rating_type (good / bad)</li>
                <li>reason (optional, short)</li>
                <li>created_at</li>
              </ul>
              <p className="font-medium mt-2">Rules</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>One review per interaction</li>
                <li>Reviews only after messaging</li>
                <li>No anonymous reviews</li>
              </ul>

              <h4 className="font-bold text-foreground mt-4">8. Safety & Abuse Model</h4>
              <p>Required for trust and moderation.</p>
              <p className="font-medium">Fields</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>report_id</li>
                <li>reported_user_id</li>
                <li>reported_by</li>
                <li>reason</li>
                <li>status (pending / reviewed)</li>
              </ul>

              <h4 className="font-bold text-foreground mt-4">9. Optional Enhancements (Post-MVP)</h4>
              <ul className="list-disc pl-5 space-y-1">
                <li>verification_status</li>
                <li>profile_visibility</li>
                <li>last_active_at</li>
              </ul>

              <h4 className="font-bold text-foreground mt-4">10. What Aviato Deliberately Excludes (for MVP)</h4>
              <ul className="list-disc pl-5 space-y-1">
                <li>Payments</li>
                <li>Ads</li>
                <li>Social feeds</li>
                <li>Long-form chat</li>
                <li>AI moderation</li>
              </ul>

              <h4 className="font-bold text-foreground mt-4">Model Summary</h4>
              <p>Aviato is built on three pillars: Availability (control), Reputation (trust), and Accountability (anti-ghosting).</p>
              <p className="italic font-medium mt-2 text-foreground">Message fewer people. Message the right ones.</p>
            </div>
            
            <button
              onClick={() => setShowModelModal(false)}
              className="w-full py-3 bg-muted text-muted-foreground rounded-lg font-medium hover:bg-accent transition-colors flex-shrink-0"
            >
              {t('common.close')}
            </button>
          </div>
        </div>
      )}

      {/* Terms of Service Modal */}
      {showTermsModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-2xl max-w-sm w-full p-6 shadow-xl max-h-[80vh] flex flex-col border border-border">
            <h3 className="text-xl font-semibold mb-4 text-foreground flex-shrink-0">{t('settings.terms')}</h3>
            
            <div className="overflow-y-auto space-y-4 mb-6 text-sm text-muted-foreground leading-relaxed pr-2">
              <p className="font-bold text-foreground">Aviato Terms of Service</p>
              <p className="italic text-muted-foreground">Tagline: Leave me alone.</p>
              <p className="text-xs text-muted-foreground">Effective Date: 06/ 01/ 26</p>
              
              <p>By using Aviato, you agree to these Terms. If you don’t agree, please don’t use the app.</p>
              
              <h4 className="font-bold text-foreground mt-4">1. What Aviato Is</h4>
              <p>Aviato is a messaging reputation and availability app designed to reduce ghosting, inbox overload, and wasted outreach.</p>
              <p>We provide tools for:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Availability signaling</li>
                <li>Messaging reputation and ratings</li>
                <li>Matching based on interests and intent</li>
              </ul>
              <p>We do not guarantee replies or outcomes.</p>

              <h4 className="font-bold text-foreground mt-4">2. Who Can Use Aviato</h4>
              <p>You must:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Be at least 13 years old</li>
                <li>Use the app legally and respectfully</li>
                <li>Provide accurate information</li>
              </ul>
              <p>You are responsible for your account activity.</p>

              <h4 className="font-bold text-foreground mt-4">3. Availability & Messaging Rules</h4>
              <ul className="list-disc pl-5 space-y-1">
                <li>You control when you are available to receive messages</li>
                <li>When your status is unavailable, you are not penalized</li>
                <li>Reputation effects only apply when you are marked available</li>
                <li>You are never forced to reply</li>
              </ul>
              <p>Aviato encourages respectful communication, not obligation.</p>

              <h4 className="font-bold text-foreground mt-4">4. Reputation, Ratings & Scores</h4>
              <p>By using Aviato, you understand that:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Ratings are based on user interactions</li>
                <li>Approval scores reflect response behavior</li>
                <li>Reputation data may be visible to other users</li>
              </ul>
              <p>We do not edit scores to favor any user.</p>
              <p>Abuse, manipulation, or fake ratings may result in penalties or removal.</p>

              <h4 className="font-bold text-foreground mt-4">5. User Conduct</h4>
              <p>You agree not to:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Harass, threaten, or abuse others</li>
                <li>Spam or send irrelevant messages</li>
                <li>Manipulate ratings or reputation systems</li>
                <li>Impersonate others</li>
                <li>Use Aviato for illegal activity</li>
              </ul>
              <p>Violations may result in suspension or account removal.</p>

              <h4 className="font-bold text-foreground mt-4">6. Content & Messages</h4>
              <ul className="list-disc pl-5 space-y-1">
                <li>You own the content you send</li>
                <li>You are responsible for what you say</li>
                <li>Aviato is not responsible for user-generated content</li>
              </ul>
              <p>We reserve the right to remove content that violates these Terms.</p>

              <h4 className="font-bold text-foreground mt-4">7. Account Suspension & Termination</h4>
              <p>We may suspend or terminate accounts if:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>These Terms are violated</li>
                <li>The platform is abused</li>
                <li>Legal or safety risks arise</li>
              </ul>
              <p>You may delete your account at any time.</p>

              <h4 className="font-bold text-foreground mt-4">8. Disclaimer</h4>
              <p>Aviato is provided “as is”.</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>We do not guarantee uninterrupted service</li>
                <li>We are not responsible for missed opportunities, lost messages, or business outcomes</li>
              </ul>
              <p>Use Aviato at your own discretion.</p>

              <h4 className="font-bold text-foreground mt-4">9. Changes to These Terms</h4>
              <p>We may update these Terms from time to time. If changes are important, we’ll notify you in the app.</p>

              <h4 className="font-bold text-foreground mt-4">10. Contact</h4>
              <p>Questions or concerns?</p>
              <p>📧 <a href="mailto:allenbrowndharak@gmail.com" className="text-blue-600 underline">allenbrowndharak@gmail.com</a></p>
              <p>+2349168839812</p>

              <h4 className="font-bold text-foreground mt-4">Plain-English Summary</h4>
              <p>Aviato helps people message better — not more.</p>
              <p>Use it respectfully, don’t game the system, and you’re good.</p>
            </div>
            
            <button
              onClick={() => setShowTermsModal(false)}
              className="w-full py-3 bg-muted text-muted-foreground rounded-lg font-medium hover:bg-accent transition-colors flex-shrink-0"
            >
              {t('common.close')}
            </button>
          </div>
        </div>
      )}

      {/* Privacy Policy Modal */}
      {showPrivacyModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-2xl max-w-sm w-full p-6 shadow-xl max-h-[80vh] flex flex-col border border-border">
            <h3 className="text-xl font-semibold mb-4 text-foreground flex-shrink-0">{t('settings.privacy')}</h3>
            
            <div className="overflow-y-auto space-y-4 mb-6 text-sm text-muted-foreground leading-relaxed pr-2">
              <p className="font-bold text-foreground">Aviato Privacy Policy</p>
              <p className="italic text-muted-foreground">Tagline: Leave me alone.</p>
              <p className="text-xs text-muted-foreground">Effective Date: 07/ 01/ 2026</p>
              
              <p>Aviato respects your privacy. This policy explains what we collect, why we collect it, and how we protect it — in plain language.</p>
              
              <h4 className="font-bold text-foreground mt-4">What We Collect</h4>
              <p>We only collect what’s needed to make Aviato work:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Basic profile info (name, username, interests)</li>
                <li>Availability status (Green, Red, etc.)</li>
                <li>Messages and interactions <strong>inside Aviato</strong></li>
                <li>Ratings, approval scores, and response timing</li>
                <li>Basic app usage data (for performance and improvement)</li>
              </ul>
              
              <p className="font-medium mt-2">We do NOT:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Read your messages for ads</li>
                <li>Sell your data</li>
                <li>Collect sensitive info (passwords, banking, government ID)</li>
              </ul>

              <h4 className="font-bold text-foreground mt-4">How We Use Your Data</h4>
              <p>We use your data to:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Show your availability status</li>
                <li>Calculate reputation and approval scores</li>
                <li>Reduce spam and ghosting</li>
                <li>Improve the app experience</li>
                <li>Keep the platform safe and fair</li>
              </ul>
              <p>That’s it.</p>

              <h4 className="font-bold text-foreground mt-4">Reputation & Transparency</h4>
              <p>Aviato has a public reputation system. By using the app, you understand that:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Your response behavior affects your score</li>
                <li>Ratings are based on real interactions</li>
                <li>Availability status protects you from penalties</li>
              </ul>
              <p>If you’re unavailable, you’re not punished.</p>

              <h4 className="font-bold text-foreground mt-4">Your Control</h4>
              <p>You’re always in charge. You can:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Change your availability anytime</li>
                <li>Edit or delete your profile</li>
                <li>Delete your account completely</li>
                <li>Opt out of notifications</li>
              </ul>
              <p>When you delete your account, your personal data is removed.</p>

              <h4 className="font-bold text-foreground mt-4">Data Protection</h4>
              <p>We use standard security practices to protect your data. No system is perfect, but we take privacy seriously and keep access limited.</p>

              <h4 className="font-bold text-foreground mt-4">Children</h4>
              <p>Aviato is not for users under 13.</p>

              <h4 className="font-bold text-foreground mt-4">Changes</h4>
              <p>If we update this policy, we’ll let you know in the app.</p>

              <h4 className="font-bold text-foreground mt-4">Contact</h4>
              <p>Questions? Data requests?</p>
              <p>📧 <a href="mailto:allenbrowndharak@gmail.com" className="text-blue-600 underline">allenbrowndharak@gmail.com</a></p>
              <p>Contact +2349168839812</p>

              <h4 className="font-bold text-foreground mt-4">One-Line Summary</h4>
              <p>Aviato only uses your data to help you avoid ghosting, control your inbox, and message better. Nothing more.</p>
            </div>
            
            <button
              onClick={() => setShowPrivacyModal(false)}
              className="w-full py-3 bg-muted text-muted-foreground rounded-lg font-medium hover:bg-accent transition-colors flex-shrink-0"
            >
              {t('common.close')}
            </button>
          </div>
        </div>
      )}


      {/* About Modal */}
      {showAboutModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-2xl max-w-sm w-full p-6 shadow-xl max-h-[80vh] flex flex-col border border-border">
            <h3 className="text-xl font-semibold mb-4 text-foreground flex-shrink-0">{t('settings.about')}</h3>
            
            <div className="overflow-y-auto space-y-4 mb-6 text-sm text-muted-foreground leading-relaxed pr-2">
              <p className="font-bold text-foreground">Aviato — Leave me alone.</p>
              
              <p>
                Aviato is a messaging reputation and availability app that stops ghosting and DM overload.
              </p>
              
              <p>
                On today’s social platforms, people are either ignored or overwhelmed. Senders waste time pitching people who never reply, while receivers drown in messages they can’t realistically handle. There’s no way to know who’s available, who’s reliable, or who’s worth messaging.
              </p>
              
              <p className="font-medium text-foreground">Aviato fixes this.</p>
              
              <p>
                The app lets users clearly set <span className="font-bold text-foreground">when and how they want to be contacted</span> using simple availability modes. Before sending a message, you can see if someone is open, busy, or completely unavailable—no guessing, no awkwardness.
              </p>
              
              <p>
                Aviato also introduces a <span className="font-bold text-foreground">messaging reputation system</span>. Users earn ratings and approval scores based on how they respond. Reliable responders stand out. Serial ghosters are visible. Ghosting finally has consequences.
              </p>
              
              <p>
                To reduce spam and wasted outreach, Aviato matches people based on shared interests and intent, so conversations are relevant from the start.
              </p>
              
              <p>
                The result is fewer ignored messages, less inbox stress, and better conversations for everyone.
              </p>
              
              <p>
                <span className="font-bold text-foreground">Aviato isn’t about messaging more.</span><br/>
                It’s about messaging the right people at the right time.
              </p>
              
              <p className="italic text-foreground font-medium">
                Leave me alone — until I’m ready.
              </p>
            </div>
            
            <button
              onClick={() => setShowAboutModal(false)}
              className="w-full py-3 bg-muted text-muted-foreground rounded-lg font-medium hover:bg-accent transition-colors flex-shrink-0"
            >
              {t('common.close')}
            </button>
          </div>
        </div>
      )}

      {/* Mode Info Modal */}
      <ModeInfoDialog 
        isOpen={showModeInfo}
        onClose={() => setShowModeInfo(false)}
      />
    </div>
  );
}

function SettingRow({ 
  icon, 
  label, 
  value, 
  onClick, 
  showArrow = true,
  isDanger = false 
}) {
  return (
    <button
      onClick={onClick}
      className={`
        w-full px-4 py-4 flex items-center justify-between 
        border-b border-border last:border-b-0
        transition-colors cursor-pointer
        ${isDanger 
          ? 'text-destructive hover:bg-destructive/10 font-medium justify-center' 
          : 'hover:bg-accent text-foreground'
        }
      `}
    >
      {!isDanger && (
        <div className="flex items-center gap-3">
          <span className="text-xl">{icon}</span>
          <span className="font-medium text-base">{label}</span>
        </div>
      )}
      
      {isDanger && (
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <span>{label}</span>
        </div>
      )}
      
      {!isDanger && (
        <div className="flex items-center gap-2">
          {value && (
            <span className="text-sm text-muted-foreground">{value}</span>
          )}
          {showArrow && (
            <ChevronRight className="w-5 h-5 text-muted-foreground/70" />
          )}
        </div>
      )}
    </button>
  );
}
