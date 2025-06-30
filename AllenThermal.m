function [w,r2,wc] = run_model2_3(x,y,z,xt,yt,wstar,wgain,rgain,zi,A,sflag)
% function [w,r2,wc] = run_model2_3(x,y,z,xt,yt,wstar,wgain,rgain,zi,A)
%
% Input: 
%   x = Aircraft x position (m)
%   y = Aircraft y position (m)
%   z = Aircraft height above ground (m)
%   xt = Vector of updraft x positions (m)
%   yt = Vector of updraft y positions (m)
%   wstar = updraft strength scale factor,(m/s)
%   wgain = Vector of perturbations from wstar (multiplier)
%   rgain = Vector of updraft radius perturbations from average (multiplier)
%   zi = updraft height (m)
%   A = Area of test space
%   sflag = 0=no sink outside of thermals, 1=sink
%
% Output: 
%   w = updraft vertical velocity (m/s)
%   r2 = outer updraft radius, m
%   wc = updraft velocity at center of thermal, m/s
%
% Michael J. Allen, NASA DFRC, 2005

% DEFINE UPDRAFT SHAPE FACTORS
r1r2shape = [0.1400 0.2500 0.3600 0.4700 0.5800 0.6900 0.8000]';
Kshape = [1.5352 2.5826 -0.0113 -0.1950 0.0008;...
          1.5265 3.6054 -0.0176 -0.1265 0.0005;...
          1.4866 4.8356 -0.0320 -0.0818 0.0001;...
          1.2042 7.7904 0.0848 -0.0445 0.0001;...
          0.8816 13.9720 0.3404 -0.0216 0.0001;...
          0.7067 23.9940 0.5689 -0.0099 0.0002;...
          0.6189 42.7965 0.7157 -0.0033 0.0001];

% CALCULATE DISTANCE TO EACH UPDRAFT
N = length(xt);
dist = zeros(1, N);
for k = 1:N
    xdsq = (x - xt(k))^2;
    ydsq = (y - yt(k))^2;
    dist(k) = sqrt(xdsq + ydsq);
end

% CALCULATE AVERAGE UPDRAFT SIZE
zzi = z / zi;
rbar = (.102 * zzi^(1/3)) * (1 - (.25 * zzi)) * zi;

% CALCULATE AVERAGE UPDRAFT STRENGTH
wtbar = (zzi^(1/3)) * (1 - 1.1 * zzi) * wstar;

% USE NEAREST UPDRAFT
[~, upused] = min(dist);

% CALCULATE INNER AND OUTER RADIUS OF ROTATED TRAPEZOID UPDRAFT
r2 = rbar * rgain(upused); % multiply by random perturbation gain
if r2 < 10
    r2 = 10; % limit small updrafts to 20m diameter
end
if r2 < 600
    r1r2 = .0011 * r2 + .14;
else
    r1r2 = .8;
end
r1 = r1r2 * r2;

% MULTIPLY AVERAGE UPDRAFT STRENGTH BY WGAIN FOR THIS UPDRAFT
wt = wtbar * wgain(upused); % add random perturbation

% CALCULATE STRENGTH AT CENTER OF ROTATED TRAPEZOID UPDRAFT
wc = (3 * wt * ((r2^3) - (r2^2) * r1)) / ((r2^3) - (r1^3));

% CALCULATE UPDRAFT VELOCITY
r = dist(upused);
rr2 = r / r2; % r/r2
if z < zi % if you are below the BL height
    if r1r2 < .5 * (r1r2shape(1) + r1r2shape(2))
        ka = Kshape(1, 1); kb = Kshape(1, 2); kc = Kshape(1, 3); kd = Kshape(1, 4);
    elseif r1r2 < .5 * (r1r2shape(2) + r1r2shape(3))
        ka = Kshape(2, 1); kb = Kshape(2, 2); kc = Kshape(2, 3); kd = Kshape(2, 4);
    elseif r1r2 < .5 * (r1r2shape(3) + r1r2shape(4))
        ka = Kshape(3, 1); kb = Kshape(3, 2); kc = Kshape(3, 3); kd = Kshape(3, 4);
    elseif r1r2 < .5 * (r1r2shape(4) + r1r2shape(5))
        ka = Kshape(4, 1); kb = Kshape(4, 2); kc = Kshape(4, 3); kd = Kshape(4, 4);
    elseif r1r2 < .5 * (r1r2shape(5) + r1r2shape(6))
        ka = Kshape(5, 1); kb = Kshape(5, 2); kc = Kshape(5, 3); kd = Kshape(5, 4);
    elseif r1r2 < .5 * (r1r2shape(6) + r1r2shape(7))
        ka = Kshape(6, 1); kb = Kshape(6, 2); kc = Kshape(6, 3); kd = Kshape(6, 4);
    else
        ka = Kshape(7, 1); kb = Kshape(7, 2); kc = Kshape(7, 3); kd = Kshape(7, 4);
    end

    in = rr2;

    % CALCULATE SMOOTH VERTICAL VELOCITY DISTRIBUTION
    ws = (1 ./ (1 + (ka .* abs(in + kc)).^kb)) + kd * in;
    ws(ws < 0) = 0; % no negative updrafts
else
    ws = 0;
end

% CALCULATE DOWNDRAFT VELOCITY AT THE EDGE OF THE UPDRAFT
if dist(upused) > r1 && rr2 < 2
    w1 = (pi / 6) * sin(pi * rr2); % downdraft, positive up
else
    w1 = 0;
end

if zzi > .5 && zzi <= .9
    swd = 2.5 * (zzi - .5); % scale factor for wd for zzi, used again later
    wd = swd * w1;
    wd(wd > 0) = 0;
else
    swd = 0;
    wd = 0;
end

w2 = ws * wc + wd * wt; % scale updraft to actual velocity

% CALCULATE ENVIRONMENT SINK VELOCITY
At = N * pi * (rbar^2); % total area taken by updrafts
if At > A
    error('Area of test space is too small');
    return;
end

if sflag
    we = -(At * wtbar * (1 - swd)) / (A - At); % environment sink rate, positive up (m/s)
    we(we > 0) = 0; % don't allow positive sink
else
    we = 0;
end

% STRETCH UPDRAFT TO BLEND WITH SINK AT EDGE
if dist(upused) > r1 % if you are outside the core
    w = w2 * (1 - we / wc) + we; % stretch
else
    w = w2;
end