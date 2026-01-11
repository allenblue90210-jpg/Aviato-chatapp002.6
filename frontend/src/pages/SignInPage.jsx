import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../contexts/AppContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Label } from '../components/ui/label';
import { useTranslation } from 'react-i18next';

const SignInPage = () => {
  const navigate = useNavigate();
  const { login, signup } = useAppContext();
  const { t } = useTranslation();
  const [isSignUp, setIsSignUp] = useState(false);
  
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (!email || !password || (isSignUp && !name)) {
        throw new Error('Please fill in all fields');
      }
      
      if (isSignUp) {
        await signup(name, email, password);
      } else {
        await login(email, password);
      }
      navigate('/match');
    } catch (err) {
      setError(err.message || (isSignUp ? 'Failed to sign up' : 'Failed to sign in'));
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsSignUp(!isSignUp);
    setError('');
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-lg border-border">
        <CardHeader className="space-y-1 text-center flex flex-col items-center">
          {/* Large Centered Logo */}
          <div className="mb-6">
             <img 
               src="https://customer-assets.emergentagent.com/job_messaging-app-253/artifacts/55vxbv1v_aviato.png" 
               alt="Aviato" 
               className="h-32 w-auto object-contain"
             />
          </div>
          
          <CardTitle className="text-3xl font-bold text-foreground">
            {isSignUp ? t('signin.create_account') : t('signin.welcome')}
          </CardTitle>
          <CardDescription className="text-muted-foreground">
            {isSignUp ? t('signin.join_community') : t('signin.sign_in_continue')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {isSignUp && (
              <div className="space-y-2">
                <Label htmlFor="name">{t('signin.full_name')}</Label>
                <Input 
                  id="name" 
                  type="text" 
                  placeholder="John Doe" 
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="h-11 bg-background text-foreground border-input"
                />
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email">{t('signin.email')}</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="name@example.com" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-11 bg-background text-foreground border-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">{t('signin.password')}</Label>
              <Input 
                id="password" 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-11 bg-background text-foreground border-input"
              />
            </div>
            
            {error && <div className="text-destructive text-sm">{error}</div>}
            
            <Button 
              type="submit" 
              className="w-full h-11 bg-primary hover:bg-primary/90 text-primary-foreground font-medium text-lg"
              disabled={loading}
            >
              {loading 
                ? (isSignUp ? t('signin.creating') : t('signin.signing_in')) 
                : (isSignUp ? t('common.next') : t('signin.title'))
              }
            </Button>
            
            <div className="relative my-4">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-2 text-muted-foreground">{t('signin.or_email')}</span>
              </div>
            </div>
            
            <div className="text-center text-sm text-muted-foreground">
              {isSignUp ? t('signin.already_account') : t('signin.dont_have_account')}{' '}
              <span 
                onClick={toggleMode}
                className="text-primary cursor-pointer hover:underline font-medium"
              >
                {isSignUp ? t('signin.title') : t('signin.create_account')}
              </span>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default SignInPage;
